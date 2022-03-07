<template>
  <div class="vm-comparison-table">
    <table ref="table"
           class="table table-bordered table-sm table-hover table-with-details table-sortable table-comparison"
           cellspacing="0">
      <caption class="d-print-none">
        <div class="d-flex justify-content-between">
          <div></div>
          <toolbar :toolbar="toolbar">
            <button-group slot="right" :options="options.agreements" />
            <button-group slot="right" :options="options.csv" />
          </toolbar>
        </div>
      </caption>
      <thead>
        <tr @click="on_sort">
          <th class="details-control" />

          <th class="range" data-sort-by="rg_id">Chapter</th>
          <th class="direction" data-sort-by="direction"
              title="Genealogical direction, potential ancestors indicated by “>”">Dir</th>
          <th class="rank" data-sort-by="rank"
              title="Ancestral rank according to the degree of agreement (Perc)">NR</th>

          <th class="perc" data-sort-by="affinity"
              title="Percentaged agreement of W1 and W2 at the variant passages attested by both (Pass)">Perc</th>
          <th class="eq" data-sort-by="equal"
              title="Number of agreements of W1 and W2 at the variant passages attested by both (Pass)">Eq</th>
          <th class="common" data-sort-by="common"
              title="Total number of passages where W1 and W2 are both extant">Pass</th>

          <th class="older" data-sort-by="older"
              title="Number of variants in W2 that are prior to those in W1">W1&lt;W2</th>
          <th class="newer" data-sort-by="newer"
              title="Number of variants in W1 that are prior to those in W2">W1&gt;W2</th>
          <th class="uncl" data-sort-by="unclear"
              title="Number of variants where no decision has been made about priority">Uncl</th>
          <th class="norel" data-sort-by="norel"
              title="Number of passages where the respective variants are unrelated">NoRel</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="r in rows">
          <tr :key="r.rg_id " :class="rowclass (r)" :data-range="r.range">
            <td class="details-control" @click="toggle_details_table (r, $event)" />

            <td class="range">{{ r.range }}</td>
            <td class="direction"
                title="Genealogical direction, potential ancestors indicated by “>”">{{ r.direction }}</td>
            <td class="rank"
                title="Ancestral rank according to the degree of agreement (Perc)">{{ r.rank }}</td>

            <td class="perc"
                title="Percentaged agreement of W1 and W2 at the variant passages attested by both (Pass)">
              {{ r.affinity }}
            </td>
            <td class="eq"
                title="Number of agreements of W1 and W2 at the variant passages attested by both (Pass)">
              {{ r.equal }}
            </td>
            <td class="common"
                title="Total number of passages where W1 and W2 are both extant">{{ r.common }}</td>

            <td class="older"
                title="Number of variants in W2 that are prior to those in W1">{{ r.newer }}</td>
            <td class="newer"
                title="Number of variants in W1 that are prior to those in W2">{{ r.older }}</td>
            <td class="uncl"
                title="Number of variants where no decision has been made about priority">{{ r.unclear }}</td>
            <td class="norel"
                title="Number of passages where the respective variants are unrelated">{{ r.norel }}</td>

          </tr>
          <tr v-if="r.child" :key="r.rg_id + '_child'" :data-range="r.range" class="child">
            <td />
            <td colspan="99">
              <comparison-details-table :ms1="ms1" :ms2="ms2" :range="r.range" />
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script>
/**
 * Comparison of 2 witnesses.  This module shows a table with a global
 * comparison of two witnesses: in how many passages do they differ, how many
 * are older / younger? There is also a drill-down table for each range with
 * more detail about the differing passages.
 *
 * @component client/comparison_table
 * @author Marcello Perathoner
 */

import tools       from 'tools';
import csv_parse   from 'csv-parse/lib/sync';
import { options } from 'widgets/options';

import sort_mixin               from 'table_sort_mixin.vue';
import toggle_mixin             from 'table_toggle_mixin.vue';
import comparison_details_table from 'comparison_details_table.vue';
import toolbar                  from 'widgets/toolbar.vue';
import button_group             from 'widgets/button_group.vue';

/**
 * Return a direction marker, <, =, or >.
 *
 * @param {object} r - Data row
 * @return {string} - Direction marker.
 */

function dir (r) {
    if (+r.older > +r.newer) {
        return '>';
    }
    if (+r.older < +r.newer) {
        return '<';
    }
    return '=';
}

/**
 * Row conversion function.  Convert numeric values to numeric types and add
 * calculated fields.
 *
 * @param  {object} d - The original row
 * @return {object}   - The converted row
 */

function row_conversion (d) {
    return {
        'rg_id'     : +d.rg_id,
        'range'     : d.range,
        'length1'   : +d.length1,
        'length2'   : +d.length2,
        'common'    : +d.common,
        'equal'     : +d.equal,
        'older'     : +d.older,
        'newer'     : +d.newer,
        'norel'     : +d.norel,
        'unclear'   : +d.unclear,
        'affinity'  : Math.round (d.affinity * 100000) / 1000,
        'rank'      : +d.rank,
        'direction' : dir (d),
        'child'     : false,
        'sorted'    : '',
    };
}

export default {
    'mixins'     : [sort_mixin, toggle_mixin],
    'components' : {
        'comparison-details-table' : comparison_details_table,
        'toolbar'                  : toolbar,
        'button-group'             : button_group,
    },
    'props' : {
        'ms1' : Object,
        'ms2' : Object,
    },
    data () {
        return {
            'rows'      : [],
            'sorted_by' : 'rg_id', // initial value
            'options'   : options,
            'summary_url'   : 'comparison-summary.csv?',
            'toolbar'   : {
                'csv' : () => this.download (), // show a download csv button
                'agreements' : () => this.switch_agreements (),
            },
        };
    },
    'watch' : {
        ms1 () {
            this.load_data ();
        },
        ms2 () {
            this.load_data ();
        },
    },
    'methods' : {
        load_data () {
            const vm = this;
            // load the csv from api
            console.log(vm.build_url());
            vm.get (vm.build_url ()).then ((response) => {
                vm.rows = csv_parse (response.data, { 'columns' : true })
                    .map (row_conversion);
                vm.sort ();
            });
        },
        switch_agreements () {
            if (this.summary_url == 'comparison-summary.csv?') {
                this.summary_url = 'comparison-agg-summary.csv?'
            }
            else {
                this.summary_url = 'comparison-summary.csv?'
            }
            this.load_data ();
        },
        download () {
            window.open (this.build_full_api_url (this.build_url (), '_blank'));
        },
        build_url () {
            return this.summary_url + tools.param ({
                'ms1' : 'id' + this.ms1.ms_id,
                'ms2' : 'id' + this.ms2.ms_id,
            });
        },
        rowclass (r) {
            return (r.older > r.newer ? 'older' : '')
                + (r.newer > r.older ? 'newer' : '')
                + (r.child ? ' shown' : '');
        },
    },
    mounted () {
        this.load_data ();
    },
};
</script>

<style lang="scss">
/* comparison_table.vue */
@import "bootstrap-custom";

table.table {
    /* also valid for details table */

    margin-top: 0 !important;
    margin-bottom: 0 !important;
    background-color: $card-bg;

    caption {
        caption-side: top;
        padding: $card-spacer-y $card-spacer-x;
        font-weight: bold;
        color: inherit;
        background-color: $card-cap-bg;
    }

    thead {
        background-color: $card-cap-bg;
    }

    tbody {
        tr.older td.direction {
            background-color: #cfc;
        }

        tr.newer td.direction {
            background-color: #fcc;
        }
    }
}

/* stylelint-disable no-descending-specificity */

div.vm-comparison-table {
    table.table-comparison {
        width: 100%;
        border-width: 0;

        th,
        td {
            text-align: right;

            &.direction {
                text-align: center;
            }
        }
    }
}

</style>
