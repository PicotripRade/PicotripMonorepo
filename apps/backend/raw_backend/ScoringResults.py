import warnings

# Suppress FutureWarnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
from backend.raw_backend.control_panel.weights import min_max_scaling_hb, min_max_scaling_lb, lb_columns, index, hb_columns, get_weights
from backend.raw_backend.control_panel.top_static_score import drop_cities_without_price
import logging

logger = logging.getLogger('django')

class ScoringResults:
    def __init__(self, input_tag, activity_tag):
        super().__init__()

        # optimizacija: blok ispod moze da se preradi sa polars-om
        try:
            t = input_tag.tag.loc[:, index+hb_columns+lb_columns].dropna()
        except:
            print("problem setting tag: ", input_tag)
            logger.error("issue when setting tag", input_tag)
            t = None

        if t is not None:
            same_value_columns = t.columns[(t.nunique() == 1)&(t.columns != 'distance from origin')]
            #ovaj dio treba detaljno prouciti
            t.drop(columns=same_value_columns, inplace=True)
            hb = list(set(hb_columns).intersection(list(t.columns)))
            t.loc[:, hb] = t[hb].apply(min_max_scaling_hb)
            t.loc[:, lb_columns] = t[lb_columns].apply(min_max_scaling_lb)
            t['index'] = t['index'].astype('int64')
            x = input_tag.tag
            x = x[x.loc[:, 'index'].isin(t.iloc[:, 0])]
            x.loc[:, hb + lb_columns + index] = t.loc[:, hb + lb_columns + index]
            x = get_weights(x, activity_tag=activity_tag)
            scored = pd.concat([x.loc[:, hb+lb_columns].sum(axis=1), input_tag.tag,], axis=1)
            scored.columns.values[0] = 'static score'

            self.scored = scored.groupby('city').head(1)

            if drop_cities_without_price:
                self.scored = self.scored.dropna().sort_values(by='static score', ascending=False)

                same_value_columns = t.columns[(t.nunique() == 1)&(t.columns != 'distance from origin')]
                #ovaj dio treba detaljno prouciti
                t.drop(columns=same_value_columns, inplace=True)
                hb = list(set(hb_columns).intersection(list(t.columns)))
                t.loc[:, hb] = t[hb].astype('float64').copy()
                t.loc[:, lb_columns] = t[lb_columns].astype('float64').copy()
                t.loc[:, hb] = t[hb].apply(min_max_scaling_hb)
                t.loc[:, lb_columns] = t[lb_columns].apply(min_max_scaling_lb)
                t['index'] = t['index'].astype('int64')
                x = input_tag.tag
                x = x[x.loc[:, 'index'].isin(t.iloc[:, 0])]
                t[hb + lb_columns + index] = t[hb + lb_columns + index].astype('float64')
                x.loc[:,hb + lb_columns + index] = x.loc[:,hb + lb_columns + index].astype('float64')
                x = get_weights(x, activity_tag='None')
                scored = pd.concat([x.loc[:, hb+lb_columns].sum(axis=1), input_tag.tag,], axis=1)
                scored.columns.values[0] = 'static score'

                self.scored = scored.groupby('city').head(1)
                self.scored = scored.groupby('airport').head(1)


            else:
                self.scored = self.scored.sort_values(by='static score', ascending=False).fillna(0)
                self.geo_tags = list(set(list(self.scored.iloc[:, 9])))
        else:
            self.scored = None
            self.geo_tags = None


