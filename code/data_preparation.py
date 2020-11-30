"""
This module is for your data cleaning.
It should be repeatable.
If you are combining different data sources you might need a few different functions

## Data links:


## SUPPORT FUNCTIONS
There can be an unlimited amount of support functions.
Each support function should have an informative name and return the partially cleaned bit of the dataset.
"""
import pandas as pd
import numpy as np


def clean_bom_title(bom):
    '''
    Remove years number, '(re-release)', '(re-issue), '(Restoration)', ' ' from the title.
    '''
    bom["cleaned_title"] = bom['title'].str.replace(r'(\(\d{4}\))', '')
    bom["cleaned_title"] = bom['cleaned_title'].str.replace(r'(\(\d{4} re-release\))', '')
    bom["cleaned_title"] = bom['cleaned_title'].str.replace(r'(\(\d{4} re-issue\))', '')
    bom["cleaned_title"] = bom['cleaned_title'].str.replace(r'(\(\d{4} Restoration\))', '')
    bom["cleaned_title"] = bom["cleaned_title"].str.strip()
    return bom


def clean_bom_gross(bom):
    '''
    Change data type to numbers, replace missing value with 0.
    '''
    bom["foreign_gross"] = bom["foreign_gross"].str.replace(',', '')
    bom['domestic_gross'] = bom['domestic_gross'].fillna(0)
    bom['foreign_gross'] = bom['foreign_gross'].fillna(0)
    bom['foreign_gross'] = bom['foreign_gross'].astype(float)
    bom['domestic_gross'] = bom['domestic_gross'].astype(int)
    bom['foreign_gross'] = bom['foreign_gross'].astype(int)
    bom['total_gross'] = bom['domestic_gross'] + bom['foreign_gross']
    bom = bom.drop(columns = ['domestic_gross', 'foreign_gross', 'title', 'total_gross'])
    return bom

    
def clean_bom(bom):
    '''
    fully clean bom.
    '''
    bom = clean_bom_title(bom)
    bom = clean_bom_gross(bom)
    return bom

    
def clean_tmdb_movies(tmdb_movies):
    '''
    create new columns.
    Merge movie by same title and re-calculate vote_average after merging.
    '''
    #tmdb_movies = tmdb_movies.drop(columns = ['Unnamed: 0', 'genre_ids','original_language', 'original_title', 'release_date','id'])
    tmdb_movies['vote_total'] = tmdb_movies['vote_average'] * tmdb_movies['vote_count']
    tmdb_movies.drop(['Unnamed: 0', 'genre_ids', 'original_language', 'popularity', 'vote_average'], inplace=True, axis=1)
    clean_tmdb = tmdb_movies.groupby('title').sum()
    clean_tmdb['vote_average'] = clean_tmdb['vote_total'] / clean_tmdb['vote_count']
    return clean_tmdb


def clean_tn_movie_budgets(tn_movie_budgets):
    '''
    Clean and change columns type to int.
    Only keep release year.
    '''
    tn_movie_budgets = tn_movie_budgets.drop(columns = ['id'])
    for column in ['production_budget', 'domestic_gross', 'worldwide_gross']:
        tn_movie_budgets[column] = tn_movie_budgets[column].str.replace('$','')
        tn_movie_budgets[column] = tn_movie_budgets[column].str.replace(',','')
        tn_movie_budgets[column] = tn_movie_budgets[column].astype('int64')
    tn_movie_budgets['release_date'] = tn_movie_budgets['release_date'].str.replace(r'.*(\d{4})', r'\1').astype('int64')
    return tn_movie_budgets.groupby(['movie', 'release_date']).sum().reset_index()
    
    
def clean_rt_info(rt_info):
    '''
    Clean rt info.
    '''
    clean_rt_info = rt_info.drop(columns = ['dvd_date', 'currency'])
    clean_rt_info['runtime'] = clean_rt_info['runtime'].str.replace(' minutes', '')
    clean_rt_info['runtime'] = clean_rt_info['runtime'].astype(float)
    clean_rt_info['genre'] = clean_rt_info['genre'].str.replace(' and ','|')
    clean_rt_info['genre'] = clean_rt_info['genre'].str.replace('|',',')
    clean_rt_info['genre'] = clean_rt_info['genre'].str.replace('Science Fiction','Sci-Fi')
    clean_rt_info = clean_rt_info.dropna(subset=['genre','runtime','theater_date'])
    return clean_rt_info


def join_bom_tn_budgets(clean_bom, clean_tn_movie_budgets):
    '''
    Join base on title and year.
    '''
    clean_bom.reset_index()
    cb1 = clean_bom.set_index(['cleaned_title', 'year'])
    ctn1 = clean_tn_movie_budgets.rename(columns={'movie': 'cleaned_title', 'release_date': 'year'})
    ctn2 = ctn1.set_index(['cleaned_title', 'year'])
    return cb1.join(ctn2, lsuffix='_bom', rsuffix='_tn', how='inner').reset_index().set_index('cleaned_title')


def join_imdb(imdb_title_basics, imdb_title_crew, imdb_title_ratings):
    '''
    Join base on tconst.
    '''
    join_imdb_tconst = imdb_title_basics.set_index('tconst').join(imdb_title_crew.set_index('tconst'), lsuffix="_basics", rsuffix="_crew", how ='inner')
    join_imdb_tconst = join_imdb_tconst.join(imdb_title_ratings.set_index('tconst'), lsuffix="_join", rsuffix="_ratings", how ='inner')
    join_imdb_tconst.set_index("primary_title", inplace=True)
    return join_imdb_tconst
    
    
def join_imdb_tconst_cleaned_data(join_imdb_tconst, cleaned_data):
    '''
    Join base on cleaned_title and year.
    '''
    jit1 = join_imdb_tconst.reset_index().rename(columns={'primary_title': 'cleaned_title', 'start_year': 'year'})
    jit2 = jit1.set_index(['cleaned_title', 'year'])
    cd1 = cleaned_data.reset_index().rename(columns={'index': 'cleaned_title'}).set_index(['cleaned_title', 'year'])
    merged_data = cd1.join(jit2, how="inner")
    merged_data.reset_index(inplace=True)
    return merged_data


def create_column(cleaned_data):
    '''
    Create new column exploring movie profitability.
    '''
    cleaned_data['profit'] = cleaned_data['worldwide_gross'] - cleaned_data['production_budget']
    cleaned_data['ROI'] = cleaned_data['profit'] / cleaned_data['production_budget']
    cleaned_data['profit_status'] = np.where(cleaned_data['ROI'] > 0, "Profit", "Non-Profit")
    return cleaned_data
    
