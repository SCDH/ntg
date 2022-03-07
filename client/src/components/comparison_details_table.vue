<template>
  <div class="vm-comparison-details slider"> <!-- table cannot animate height -->
    <table ref="table" cellspacing="0" width="100%"
           class="table table-bordered table-condensed table-hover table-sortable table-comparison-details">
      <caption>
        <div class="d-flex justify-content-between">
          <div class="caption">
            Detailed Comparison of {{ ms1.hs }} and {{ ms2.hs }} in Chapter {{ range }}
          </div>
          <toolbar :toolbar="toolbar">
            <button-group slot="right" :options="options.agreements" />
            <button-group slot="right" :options="options.csv" />
          </toolbar>
        </div>
      </caption>
      <thead>
        <tr @click="on_sort">
          <th class="passage" data-sort-by="pass_id">Passage</th>
          <th class="lesart lesart1" data-sort-by="lesart1">Lesart</th>
          <th class="ms ms1" data-sort-by="labez_clique1">{{ ms1.hs }}</th>
          <th class="direction" data-sort-by="direction">Dir</th>
          <th class="ms ms2" data-sort-by="labez_clique2">{{ ms2.hs }}</th>
          <th class="lesart lesart2" data-sort-by="lesart2">Lesart</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in rows" :key="r.pass_id" :class="(r.newer ? 'newer' : '') + (r.older ? 'older' : '')">
          <td class="passage">
            <router-link :to="{ 'name' : 'coherence', 'params' : { 'passage_or_id' : r.pass_id }}">{{ r.pass_hr }}</router-link>
          </td>
          <td class="lesart lesart1">{{ r.lesart1 }}</td>
          <td class="ms ms1">{{ r.labez_clique1 }}</td>
          <td class="direction">{{ r.direction }}</td>
          <td class="ms ms2">{{ r.labez_clique2 }}</td>
          <td class="lesart lesart2">{{ r.lesart2 }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
/**
 * Comparison of 2 witnesses.  This module shows a drill-down table for each range with
 * more detail about the differing passages.
 *
 * @component client/comparison_details_table
 * @author Marcello Perathoner
 */

import csv_parse    from 'csv-parse/lib/sync';

import sort_mixin   from 'table_sort_mixin.vue';
import tools        from 'tools';
import button_group from 'widgets/button_group.vue';
import toolbar      from 'widgets/toolbar.vue';
import { options }  from 'widgets/options';


/**
 * Return a direction marker: <, >, NoRel or Uncl.
 *
 * @param {object} r - The data row
 * @return {string}  - Direction marker.
 */

function dir (r) {
    if (r.older) {
        return '>';
    }
    if (r.newer) {
        return '<';
    }
    if (r.unclear) {
        return 'Uncl';
    }
    return 'NoRel';
}

/**
 * Detail row conversion function.  Convert numeric values to numeric types
 * and add calculated fields.
 *
 * @param  {object} d - The original row
 * @return {object}   - The converted row
 */

function row_conversion (d) {
    let r = {
        'pass_id'       : +d.pass_id,
        'pass_hr'       : d.pass_hr,
        'labez_clique1' : d.labez_clique1,
        'lesart1'       : d.lesart1,
        'labez_clique2' : d.labez_clique2,
        'lesart2'       : d.lesart2,
        'older'         : d.older   === 'True',
        'newer'         : d.newer   === 'True',
        'norel'         : d.norel   === 'True',
        'unclear'       : d.unclear === 'True',
    };
    r.direction = dir (r);
    return r;
}

export default {
    'props'      : ['ms1', 'ms2', 'range'],
    'mixins'     : [sort_mixin],
    'components' : {
        'button-group' : button_group,
        'toolbar'      : toolbar,
    },
    data () {
        return {
            'rows'      : [],
            'sorted_by' : 'pass_id',
            'detail_url': 'comparison-detail.csv',
            'options'   : options,
            'toolbar'   : {
                'csv' : () => this.download (), // show a download csv button
                'agreements' : () => this.switch_agreements (),
            },
        };
    },
    'methods' : {
        load_data () {
            const vm = this;
            vm.get (vm.build_url ()).then ((response) => {
                vm.rows = csv_parse (response.data, { 'columns' : true })
                    .map (row_conversion);
                vm.sort ();
                vm.$nextTick (() => {
                    tools.slide_fade_in (vm.$el);
                });
            });
        },
        switch_agreements () {
            if (this.detail_url == 'comparison-detail.csv') {
                this.detail_url = 'comparison-detail-agg.csv'
            }
            else {
                this.detail_url = 'comparison-detail.csv'
            }
            this.load_data ();
        },
        build_url (page = this.detail_url) {
            return page + '?' + tools.param ({
                'ms1'   : 'id' + this.ms1.ms_id,
                'ms2'   : 'id' + this.ms2.ms_id,
                'range' : this.range,
            });
        },
        download () {
            window.open (this.build_full_api_url (this.build_url (), '_blank'));
        },
    },
    mounted () {
        this.load_data ();
    },
};
</script>

<style lang="scss">
/* comparison_table_details.vue */
@import "bootstrap-custom";

div.vm-comparison-details {
    height: 0;
    overflow: hidden;
    opacity: 0;

    table.table-comparison-details {
        border-width: 0;

        caption {
            border-bottom: $table-border-width solid $table-border-color;
        }

        th,
        td {
            text-align: left;

            &[data-sort-by] {
                padding-left: 1.5em;
            }

            &.passage {
                width: 15%;
            }

            &.direction {
                text-align: center;
                padding-left: 0;
                width: 5%;
            }

            &.lesart {
                width: 35%;
            }
        }
    }
}
</style>
