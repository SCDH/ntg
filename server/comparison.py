# -*- encoding: utf-8 -*-

"""The comparison function of the API server for CBGM."""

import collections

import flask
from flask import request, current_app

from ntg_common.db_tools import execute

from login import auth
from helpers import csvify, parameters, Passage, Manuscript


bp = flask.Blueprint ('comparison', __name__)


def init_app (_app):
    """ Initialize the flask app. """


_ComparisonRow = collections.namedtuple (
    'ComparisonRow',
    'rg_id, range, common, equal, older, newer, unclear, affinity, rank, length1, length2'
)


class _ComparisonRowCalcFields (_ComparisonRow):
    __slots__ = ()

    _fields = _ComparisonRow._fields + ('norel', )

    @property
    def norel (self):
        return self.common - self.equal - self.older - self.newer - self.unclear

    def _asdict (self):
        return collections.OrderedDict (zip (self._fields, self + (self.norel, )))


def comparison_summary ():
    """Output comparison of 2 witnesses, chapter summary.

    Outputs a summary of the differences between 2 manuscripts, one summary row
    per chapters.

    """

    with current_app.config.dba.engine.begin () as conn:
        ms1 = Manuscript (conn, request.args.get ('ms1') or 'A')
        ms2 = Manuscript (conn, request.args.get ('ms2') or 'A')

        res = execute (conn, """
        (WITH ranks AS (
          SELECT ms_id1, ms_id2, rg_id, rank () OVER (PARTITION BY rg_id ORDER BY affinity DESC) AS rank, affinity
          FROM affinity aff
          WHERE ms_id1 = :ms_id1
            AND {prefix}newer > {prefix}older
          ORDER BY affinity DESC
        )

        SELECT a.rg_id, a.range, a.common, a.equal,
               a.older, a.newer, a.unclear, a.affinity, r.rank, ms1_length, ms2_length
        FROM {view} a
        JOIN ranks r     USING (rg_id, ms_id1, ms_id2)
        WHERE a.ms_id1 = :ms_id1 AND a.ms_id2 = :ms_id2
        )

        UNION

        (WITH ranks2 AS (
          SELECT ms_id1, ms_id2, rg_id, rank () OVER (PARTITION BY rg_id ORDER BY affinity DESC) AS rank, affinity
          FROM affinity aff
          WHERE ms_id2 = :ms_id2
            AND {prefix}newer < {prefix}older
          ORDER BY affinity DESC
        )

        SELECT a.rg_id, a.range, a.common, a.equal,
               a.older, a.newer, a.unclear, a.affinity, r.rank, ms1_length, ms2_length
        FROM {view} a
        JOIN ranks2 r USING (rg_id, ms_id1, ms_id2)
        WHERE a.ms_id1 = :ms_id1 AND a.ms_id2 = :ms_id2
        )

        UNION

        SELECT a.rg_id, a.range, a.common, a.equal,
               a.older, a.newer, a.unclear, a.affinity, NULL, ms1_length, ms2_length
        FROM {view} a
        WHERE a.ms_id1 = :ms_id1 AND a.ms_id2 = :ms_id2 AND a.newer = a.older

        ORDER BY rg_id
        """, dict (parameters, ms_id1 = ms1.ms_id, ms_id2 = ms2.ms_id,
                   view = 'affinity_p_view', prefix = 'p_'))

        return list (map (_ComparisonRowCalcFields._make, res))


_ComparisonDetailRow = collections.namedtuple (
    'ComparisonDetailRow',
    'pass_id begadr endadr labez_clique1 lesart1 labez_clique2 lesart2 older newer unclear'
)

class _ComparisonDetailRowCalcFields (_ComparisonDetailRow):
    __slots__ = ()

    _fields = _ComparisonDetailRow._fields + ('pass_hr', 'norel')

    @property
    def pass_hr (self):
        return Passage.static_to_hr (self.begadr, self.endadr)

    @property
    def norel (self):
        return not (self.older or self.newer or self.unclear)

    def _asdict (self):
        return collections.OrderedDict (zip (self._fields, self + (self.pass_hr, self.norel)))


def comparison_detail ():
    """Output comparison of 2 witnesses, chapter detail.

    Outputs a detail of the differences between 2 manuscripts in one chapter.
    """

    with current_app.config.dba.engine.begin () as conn:
        ms1 = Manuscript (conn, request.args.get ('ms1') or 'A')
        ms2 = Manuscript (conn, request.args.get ('ms2') or 'A')
        range_ = request.args.get ('range') or 'All'

        res = execute (conn, """
        SELECT p.pass_id, p.begadr, p.endadr, v1.labez_clique, v1.lesart,
                                              v2.labez_clique, v2.lesart,
          is_p_older (p.pass_id, v1.labez, v1.clique, v2.labez, v2.clique) AS older,
          is_p_older (p.pass_id, v2.labez, v2.clique, v1.labez, v1.clique) AS newer,
          is_p_unclear (p.pass_id, v1.labez, v1.clique) OR
          is_p_unclear (p.pass_id, v2.labez, v2.clique) AS unclear
        FROM (SELECT * FROM ranges WHERE range = :range_) r
          JOIN passages p ON (r.passage @> p.passage )
          JOIN apparatus_cliques_view v1 USING (pass_id)
          JOIN apparatus_cliques_view v2 USING (pass_id)
        WHERE v1.ms_id = :ms1 AND v2.ms_id = :ms2
          AND v1.labez != v2.labez AND v1.labez !~ '^z' AND v2.labez !~ '^z'
          AND v1.cbgm AND v2.cbgm
        ORDER BY p.pass_id
        """, dict (parameters, ms1 = ms1.ms_id, ms2 = ms2.ms_id, range_ = range_))

        return list (map (_ComparisonDetailRowCalcFields._make, res))

def comparison_detail_agg ():
    """Output comparison of 2 witnesses, chapter detail.

    Outputs a detail of the differences between 2 manuscripts in one chapter.
    """

    with current_app.config.dba.engine.begin () as conn:
        ms1 = Manuscript (conn, request.args.get ('ms1') or 'A')
        ms2 = Manuscript (conn, request.args.get ('ms2') or 'A')
        range_ = request.args.get ('range') or 'All'

        res = execute (conn, """
        SELECT p.pass_id, p.begadr, p.endadr, v1.labez_clique, v1.lesart,
                                              v2.labez_clique, v2.lesart,
          is_p_older (p.pass_id, v1.labez, v1.clique, v2.labez, v2.clique) AS older,
          is_p_older (p.pass_id, v2.labez, v2.clique, v1.labez, v1.clique) AS newer,
          is_p_unclear (p.pass_id, v1.labez, v1.clique) OR
          is_p_unclear (p.pass_id, v2.labez, v2.clique) AS unclear
        FROM (SELECT * FROM ranges WHERE range = :range_) r
          JOIN passages p ON (r.passage @> p.passage )
          JOIN apparatus_cliques_view v1 USING (pass_id)
          JOIN apparatus_cliques_view v2 USING (pass_id)
        WHERE v1.ms_id = :ms1 AND v2.ms_id = :ms2
          AND v1.labez !~ '^z' AND v2.labez !~ '^z'
          AND v1.cbgm AND v2.cbgm
        ORDER BY p.pass_id
        """, dict (parameters, ms1 = ms1.ms_id, ms2 = ms2.ms_id, range_ = range_))

        return list (map (_ComparisonDetailRowCalcFields._make, res))


@bp.route ('/comparison-summary.csv')
def comparison_summary_csv ():
    """Endpoint. Serve a CSV table. (see also :func:`comparison_summary`)"""

    auth ()

    return csvify (_ComparisonRowCalcFields._fields, comparison_summary ())


@bp.route ('/comparison-detail.csv')
def comparison_detail_csv ():
    """Endpoint. Serve a CSV table. (see also :func:`comparison_detail`)"""

    auth ()

    return csvify (_ComparisonDetailRowCalcFields._fields, comparison_detail ())


@bp.route ('/comparison-detail-agg.csv')
def comparison_detail_csv_agg ():
    """Endpoint. Serve a CSV table. (see also :func:`comparison_detail`)"""

    auth ()

    return csvify (_ComparisonDetailRowCalcFields._fields, comparison_detail_agg ())
