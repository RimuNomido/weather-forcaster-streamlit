import altair as alt
import streamlit as st
import pandas as pd
import os
import httpx

FASTAPI_URL = os.getenv('FASTAPI_URL', 'http://localhost:8000')

st.set_page_config(page_title="Погода", page_icon="⛅")  # если ещё не добавили

import streamlit as st

st.markdown(
    """
    <style>
        .stAppDeployButton {
            visibility: hidden;
        }
        [data-testid="stStatusWidget"] {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if 'current_view' not in st.session_state:
    st.session_state.current_view = None

if 'cleaner_show' not in st.session_state:
    st.session_state.cleaner_show = False

if 'history_cleaned' not in st.session_state:
    st.session_state.history_cleaned = False

if 'download_stats_show' not in st.session_state:
    st.session_state.download_stats_show = False

if 'weather_data' not in st.session_state:
    st.session_state.weather_data = None

def hide_cleaner_button():
    st.session_state.current_view = None
    st.session_state.cleaner_show = False
    st.session_state.cleaner_show = False

st.title('⛅Погода')

with st.container(border=True):
    st.header('Узнать погоду')
    city = st.text_input('Введите город', on_change=hide_cleaner_button)

    col_left, col_mid, col_right = st.columns([6.7, 1.5, 1.27])
    with col_mid:
        if st.button('Статистика'):
            st.session_state.current_view = 'stats'
            st.session_state.history_cleaned = False
            st.session_state.cleaner_show = False
    with col_left:
        if st.button('Поиск'):
            st.session_state.current_view = 'search'
            st.session_state.history_cleaned = False

    with col_right:
        if st.button('История'):
            st.session_state.current_view = 'history'
            st.session_state.history_cleaned = False

    if st.session_state.current_view == 'stats':
        st.subheader('📊 Статистика')
        response = httpx.get(f'{FASTAPI_URL}/stats/12345')
        data = response.json()

        if data['total_queries'] == 0:
            with st.container(border=True):
                st.write('Нет данных для статистики')
        else:
            top_cities = data['top_cities']
            
            with st.container(border=True):

                df = pd.DataFrame(top_cities)
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X('city:N', title='Город'),
                    y=alt.X('count:Q', title='Количество'),
                    color=alt.Color('city', title='Всего')
                ).properties(title='Топ городов по запросам')
                
                st.altair_chart(chart, width='stretch')

            with st.container(border=True):
                if data['total_queries'] == 0:
                    st.write('Нет запросов для статистики')
                    st.session_state.download_stats_show = False
                else:
                    st.write(f'**Всего запросов:** {data['total_queries']}')
                    st.write(f'**Чаще всего вы искали погоду в:**')
                    for city_info in data['top_cities']:
                        st.write(f'- {city_info['city']}: {city_info['count']} раз')
                    st.session_state.download_stats_show = True

                if st.session_state.download_stats_show is True:
                    st.download_button(label='Нажмите, чтобы скачать статистику', data = data['stats'], file_name='stats.txt')

    if st.session_state.current_view == 'search':
        st.subheader('🔎 Результат поиска')
        with st.container(border=True):
            if len(city) == 0:
                st.write('Поле ввода не должно быть пустым')
            else:
                with st.spinner('Загрузка...'):
                    data = httpx.get(f'{FASTAPI_URL}/weather/{city}').json()
                weather = data['weather']
                data = {
                    'user_id': 12345,
                    'city': city,
                    'weather': data['row']
                }
                httpx.post(f'{FASTAPI_URL}/history', json=data)
                st.session_state.history_cleaned = False
                st.success(weather)

    if st.session_state.current_view == 'history':
        st.subheader('📜 История запросов')
        with st.container(border=True):
            st.session_state.history_cleaned = False
            with st.spinner('Загрузка...'):
                response = httpx.get(f'{FASTAPI_URL}/history/12345')
    
            data = response.json()
            if data['total'] == 0:
                st.write('История запросов пуста')
            else:
                st.write('### Общее количество запросов: ', data['total'])
                st.write(data['history'])
                st.session_state.cleaner_show = True
    
        if st.session_state.cleaner_show:
            clear_history_button = st.button('Очистить историю')
            if clear_history_button:
                with st.spinner('Загрузка...'):
                    response = httpx.delete(f'{FASTAPI_URL}/history/12345')
                st.session_state.history_cleaned = True
                st.session_state.cleaner_show = False
                st.session_state.current_view = None
                st.rerun()
        
if st.session_state.history_cleaned:
    st.success('История очищена')