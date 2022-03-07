const options = {
    'type' : [
        { 'text' : 'Rel', 'value' : 'rel', 'title' : 'Show all relatives.'    },
        { 'text' : 'Anc', 'value' : 'anc', 'title' : 'Show only ancestors.'   },
        { 'text' : 'Des', 'value' : 'des', 'title' : 'Show only descendants.' },
    ],
    'limit' : [
        { 'text' : '10',  'value' : '10', 'title' : 'Show 10 items.'  },
        { 'text' : '20',  'value' : '20', 'title' : 'Show 20 items.'  },
        { 'text' : 'All', 'value' : '0',  'title' : 'Show all items.' },
    ],
    'include' : [
        { 'text' : 'A',   'value' : 'A',  'title' : 'Include the "A" text.'       },
        { 'text' : 'MT',  'value' : 'MT', 'title' : 'Include the Byzantine text.' },
        { 'text' : 'Fam', 'value' : 'F',  'title' : 'Include text families.'      },
    ],
    'include_z' : [
        { 'text' : 'A',   'value' : 'A',  'title' : 'Include the "A" text.'              },
        { 'text' : 'MT',  'value' : 'MT', 'title' : 'Include the Byzantine text.'        },
        { 'text' : 'Fam', 'value' : 'F',  'title' : 'Include text families.'             },
        { 'text' : 'Z',   'value' : 'Z',  'title' : 'Include mss. lacking this passage.' },
    ],
    'mode' : [
        { 'text' : 'Sim', 'value' : 'sim', 'title' : 'Use simple priority calculation.'    },
        { 'text' : 'Rec', 'value' : 'rec', 'title' : 'Use recursive priority calculation.' },
    ],
    'cliques' : [
        {
            'text'  : 'Splits',
            'value' : 'cliques',
            'title' : 'Show split attestations.'
        },
    ],
    'ortho' : [
        {
            'text'  : 'Ortho',
            'value' : 'ortho',
            'title' : 'Show orthographic variations.'
        },
    ],
    'fragments' : [
        {
            'text'  : 'Frag',
            'value' : 'fragments',
            'title' : 'Include document fragments.'
        },
    ],
    'checks' : [
        {
            'text'  : 'CHK',
            'value' : 'checks',
            'title' : 'Perform congruence checks.'
        },
    ],
    'png_dot' : [
        {
            'text'  : 'PNG',
            'value' : 'png',
            'title' : 'Download this graph in PNG format.'
        },
        {
            'text'  : 'DOT',
            'value' : 'dot',
            'title' : 'Download this graph in GraphViz DOT format.'
        },
    ],
    'csv' : [
        {
            'text'  : 'CSV',
            'value' : 'csv',
            'title' : 'Download this table in CSV format.'
        },
    ],
    'agreements' : [
        {
            'text'  : 'Show/Hide Agreements',
            'value' : 'agreements',
            'title' : 'Show or hide agreements'
        },
    ],
    'find_relatives' : [
        {
            'text'  : 'Find Relatives',
            'value' : 'rel',
            'title' : 'List all mss. that offer a certain reading at this passage.',
        },
    ],
    'labez' : {
        'title'  : 'Select a variant.',
        'reduce' : 'a',
        'prefix' : [],
        'suffix' : [],
    },
    'labez_all' : {
        'title'  : 'Select a variant.',
        'reduce' : 'all+lac',
        'prefix' : [{ 'labez' : 'all',     'labez_i18n' : 'All'     }],
        'suffix' : [{ 'labez' : 'all+lac', 'labez_i18n' : 'All+Lac' }],
    },
    'hyp_a' : {
        'title'  : 'Select a different reading for "A".',
        'reduce' : 'a',
        'prefix' : [],
        'suffix' : [],
    },
}

export { options };
