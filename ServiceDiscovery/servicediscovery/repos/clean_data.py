# *******************************************************************************
# Copyright (C) 2022 AIR Institute
#
# This program and the accompanying materials are made
# available under the terms of the Eclipse Public License 2.0
# which is available at https://www.eclipse.org/legal/epl-2.0/
#
# SPDX-License-Identifier: EPL-2.0
#
# Contributors:
#    David Berrocal Macías (@dabm-git) - initial API and implementation
# *******************************************************************************

import pandas as pd
import os
import glob
from langdetect import detect
import re
import numpy as np
from utils import SCRUtils


class ServiceCrawledDataPreProcess:

    df_crawled = pd.DataFrame()

    def clean_export_data(self, data_list, file_name):
        # convert the list data_list to dataframe
        df = pd.DataFrame(data_list, columns=[
            "id",
            "name",
            "user_id",
            "registry_id",
            "git_credentials_id",
            "url",
            "description",
            "is_public",
            "licence",
            "framework",
            "created",
            "updated",
            "stars",
            "forks",
            "watchers",
            "deployable",
            "keywords",
        ])

        if df is not None:
            self.df_crawled = df

        # check if the description is more than 10 characters, else skip it
        if (df['description'].str.len().max() > 10):
            # filter to have just english data in description
            self.df_crawled = self.filter_en_data("description")
            # filter Nan, null values
            self.df_crawled = self.remove_null("description")
            # filter html
            self.df_crawled = self.filter_HTML_data("description")
            # filter url
            self.df_crawled = self.filter_URL_data("description")
            # filter based on len
            self.df_crawled = self.filter_based_len("description")

        self.df_crawled = self.remove_null("keywords")
        # Export the dataframe to csv file
        SCRUtils.export_csv(self.df_crawled, file_name, True, True)

        return self.df_crawled.to_dict(orient='records')

    def load_crawled_data(self):
        # ,full_name,link,description,stars,forks,watchers,updated_on,keywords,source
        df_main = pd.DataFrame(columns=[
                               'full_name', 'link', 'description', 'stars', 'forks', 'watchers', 'keywords', 'source'])

        path = os.getcwd() + git_data_Folder
        csv_files = glob.glob(os.path.join(path, "Git*.csv"))

        # loop over the list of csv files
        for f in csv_files:
            # read the csv file
            df_git = pd.read_csv(f)
            df_git = df_git.loc[:, ~df_git.columns.str.contains('^Unnamed')]
            df_git2 = df_git[['full_name', 'link', 'description',
                              'stars', 'forks', 'watchers', 'keywords', 'source']]
            frames = [df_git2, df_main]
            df_main = pd.concat(frames)
            print('File Name:', f.split("\\")[-1])
            print('Content:')
            display(df_git)
        self.df_crawled = df_main
        return self.df_crawled

    def select_baseon_keyword(self, keyword, df=None):
        if df is not None:
            self.df_crawled = df

        self.df_crawled = self.df_crawled[self.df_crawled.keywords.isin(
            keyword)]

        return self.df_crawled

    def Replace_keywords_to_category(self, replacement, df=None):
        if df is not None:
            self.df_crawled = df

        self.df_crawled['keywords'] = self.df_crawled['keywords'].replace(
            replacement, regex=True)
        return self.df_crawled

    # filter english text:
    def detect_en(self, text):
        try:
            return detect(text) == 'en'
        except:
            return False

    def filter_en_data(self, Clm_name, df=None):
        if df is not None:
            self.df_crawled = df

        if Clm_name in self.df_crawled:
            return self.df_crawled[self.df_crawled[Clm_name].apply(self.detect_en)]
        return self.df_crawled

    # preprocess and delete html tags
    def removeHTMLTags(self, string):
        return re.sub('<.*?>', '', string)

    def filter_HTML_data(self, Clm_name, df=None):
        if df is not None:
            self.df_crawled = df
        if Clm_name in self.df_crawled.columns:
            self.df_crawled[Clm_name] = self.df_crawled[Clm_name].astype(
                str).apply(self.removeHTMLTags)
            return self.df_crawled
        return self.df_crawled

    def filter_URL_data(self, Clm_name, df=None):
        if df is not None:
            self.df_crawled = df
        if Clm_name in self.df_crawled.columns:
            self.df_crawled[Clm_name] = self.df_crawled[Clm_name].str.replace(
                'http\S+|www.\S+', '', case=False, regex=True)
            return self.df_crawled
        return self.df_crawled

    def filter_based_len(self, Clm_name, len=50, df=None):
        if df is not None:
            self.df_crawled = df
        if not Clm_name in self.df_crawled.columns:
            return self.df_crawled

        self.df_crawled['length'] = self.df_crawled[Clm_name].str.len()
        self.df_crawled.sort_values('length', ascending=False, inplace=True)

        self.df_crawled['length'] = self.df_crawled['length'].astype('Int64')
        self.df_crawled = self.df_crawled[~(self.df_crawled['length'] <= 50)]
        self.df_crawled = self.df_crawled.drop(
            ['index', 'Unnamed: 0'], axis=1, errors='ignore')
        # remove null
        self.df_crawled = self.df_crawled.replace(
            np.nan, '', regex=True)  # All data frame
        # reindex
        self.df_crawled.reset_index(inplace=True)
        return self.df_crawled

    def filter_based_len(self, Clm_name, len=50, df=None):
        if df is not None:
            self.df_crawled = df
        self.df_crawled['length'] = self.df_crawled[Clm_name].str.len()
        return self.df_crawled

    def remove_null(self, Clm_name, len=50, df=None):
        if df is not None:
            self.df_crawled = df
        # check if Clm_name exists in dataframe
        if Clm_name in self.df_crawled.columns:
            self.df_crawled = self.df_crawled[self.df_crawled[Clm_name].isnull(
            ) == False]
            self.df_crawled = self.df_crawled[self.df_crawled[Clm_name].isna(
            ) == False]
            return self.df_crawled
        return self.df_crawled

    def map_clm_name(self, map_clm, df=None):
        if df is not None:
            self.df_crawled = df
        df_temp = self.df_crawled
        df_temp = df_temp.rename(map_clm)
        self.df_crawled = df_temp
        return self.df_crawled
