#  file explanation...

#  geo filters

#  geo parameter defines allowed geolocations (country, group of countries, continent )

geo_location = {
                'africa': ['AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CG', 'CD', 'CI',
                           'DJ', 'EG', 'GQ', 'ER', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW', 'KE', 'LS', 'LR',
                           'LY', 'MG', 'ML', 'MW', 'MR', 'MU', 'YT', 'MA', 'MZ', 'NA', 'NE', 'NG', 'RE',
                           'RW', 'ST', 'SN', 'SC', 'SL', 'SO', 'ZA', 'SS', 'SD', 'SZ', 'TZ', 'TG', 'TN',
                           'UG', 'EH', 'ZM', 'ZW'
                           ],

                'asia': ['AF', 'AS', 'AU', 'BD', 'BT', 'IO', 'BN', 'KH', 'CN', 'CX', 'CC', 'CK', 'TL', 'FJ',
                         'PF', 'TF', 'GU', 'HK', 'IN', 'ID', 'JP', 'KI', 'KP', 'KR', 'LA', 'MO', 'MY', 'MV',
                         'MH', 'FM', 'MN', 'MM', 'NR', 'NP', 'NC', 'NZ', 'NU', 'NF', 'MP', 'PK', 'PW', 'PG',
                         'PH', 'PN', 'WS', 'SG', 'SB', 'LK', 'TW', 'TH', 'TK', 'TO', 'TV', 'VU', 'VN', 'WF'
                         ],

                'south_america': ['AG', 'BL', 'CK', 'FG', 'PY', 'SR', 'VE', 'BO', 'CL', 'EC', 'GY', 'PE', 'UY'],

                'europe': ['AL', 'AD', 'AM', 'AT', 'BY', 'BE', 'BA', 'BG', 'CH', 'CY', 'CZ', 'DE', 'DK', 'EE',
                           'ES', 'FO', 'FI', 'FR', 'GB', 'GE', 'GI', 'GR', 'HU', 'HR', 'IE', 'IS', 'IT', 'LI',
                           'LT', 'LU', 'LV', 'MC', 'ME', 'MK', 'MT', 'NO', 'NL', 'PL', 'PT', 'RO', 'RS', 'RU',
                           'SE', 'SI', 'SK', 'SM', 'TR', 'UA', 'VA'
                           ],

                'north_america': ['AI', 'AG', 'AW', 'BS', 'BB', 'BZ', 'BM', 'BQ', 'VG', 'CA', 'KY', 'CR', 'CU', 'CW',
                                  'DM', 'DO', 'SV', 'GL', 'GD', 'GP', 'GT', 'HT', 'HN', 'JM', 'MQ', 'MX', 'PM', 'MS',
                                  'CW', 'KN', 'NI', 'PA', 'PR', 'BQ', 'BQ', 'SX', 'KN', 'LC', 'PM', 'VC', 'TT', 'TC',
                                  'US', 'VI'
                                  ],

                'all_countries': ['AO', 'BJ', 'BW', 'BF', 'BI', 'CM', 'CV', 'CF', 'TD', 'KM', 'CG', 'CD', 'CI',
                                  'DJ', 'EG', 'GQ', 'ER', 'ET', 'GA', 'GM', 'GH', 'GN', 'GW', 'KE', 'LS', 'LR',
                                  'LY', 'MG', 'ML', 'MW', 'MR', 'MU', 'YT', 'MA', 'MZ', 'NA', 'NE', 'NG', 'RE',
                                  'RW', 'ST', 'SN', 'SC', 'SL', 'SO', 'ZA', 'SS', 'SD', 'SZ', 'TZ', 'TG', 'TN',
                                  'UG', 'EH', 'ZM', 'ZW', 'AF', 'AS', 'AU', 'BD', 'BT', 'BN', 'KH', 'CN', 'VI',
                                  'CX', 'CC', 'CK', 'TL', 'FJ', 'PF', 'TF', 'GU', 'HK', 'IN', 'ID', 'JP', 'KI',
                                  'KP', 'KR', 'LA', 'MO', 'MY', 'MV', 'MH', 'FM', 'MN', 'MM', 'NR', 'NP', 'NC',
                                  'NZ', 'NU', 'NF', 'MP', 'PK', 'PW', 'PG', 'PH', 'PN', 'WS', 'SG', 'SB', 'LK',
                                  'TW', 'TH', 'TK', 'TO', 'TV', 'VU', 'VN', 'WF', 'AG', 'BL', 'CK', 'FG', 'PY',
                                  'SR', 'VE', 'BO', 'CL', 'EC', 'GY', 'PE', 'UY', 'AL', 'AD', 'AM', 'AT', 'BY',
                                  'BE', 'BA', 'BG', 'CH', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FO', 'FI', 'FR',
                                  'GB', 'GE', 'GI', 'GR', 'HU', 'HR', 'IE', 'IS', 'IT', 'LI', 'LT', 'LU', 'LV',
                                  'MC', 'US', 'MK', 'MT', 'NO', 'NL', 'PL', 'PT', 'RO', 'RS', 'RU', 'SE', 'SI',
                                  'SK', 'SM', 'TR', 'UA', 'VA', 'AI', 'AG', 'AW', 'BS', 'BB', 'BZ', 'BM', 'BQ',
                                  'VG', 'CA', 'KY', 'CR', 'CU', 'CW', 'DM', 'DO', 'SV', 'GL', 'GD', 'GP', 'GT',
                                  'HT', 'HN', 'JM', 'MQ', 'MX', 'PM', 'MS', 'CW', 'KN', 'NI', 'PA', 'PR', 'BQ',
                                  'BQ', 'SX', 'KN', 'LC', 'PM', 'VC', 'TT', 'TC', 'ME'
                                  ]
                }
