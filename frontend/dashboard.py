import altair as alt
import streamlit as st
import pandas as pd
import os
import httpx
import json

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

if 'sign_in_success' not in st.session_state:
    st.session_state.sign_in_success = False

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

def switch_view(to_view=None):
    st.session_state.current_view = to_view
    st.session_state.cleaner_show = False
    st.session_state.history_cleaned = False
    st.session_state.download_stats_show = False

def try_to_int(text):
    try:
        return int(text)
    except ValueError:
        return None
    
col_title, col_account, col_out = st.columns([0.62, 0.27, 0.11])

with col_title:
    st.markdown('<div style="margin-top: 2.35;"></div>', unsafe_allow_html=True)
    st.title('⛅Погода')

with col_out:
    button_placeholder = st.empty()
with col_account:
    account_placeholder = st.empty()

auth_placeholder = st.empty()
error_placeholder = st.empty()

if not st.session_state.sign_in_success:
    with auth_placeholder.container(border=True):
        st.write('### Введите id:')
        user_id = st.text_input(label='', label_visibility='collapsed', max_chars=9)
        col_void, col_sign = st.columns([0.89, 0.11])
        with col_sign:
            if st.button('Войти', width='content'):
                user_id = try_to_int(user_id)
                if not user_id is None and user_id > 0:
                    st.session_state.user_id = user_id
                    st.session_state.sign_in_success = True
                    st.rerun()
                else:
                    with error_placeholder.container():
                        st.error('id должен быть целым положительным числом', width='stretch')

if st.session_state.sign_in_success:
    with button_placeholder.container():
        st.markdown('<div style="margin-top: 3rem;"></div>', unsafe_allow_html=True)
        if st.button('Выход', width='stretch'):
            st.session_state.sign_in_success = False
            st.session_state.user_id = None
            st.rerun()
    with account_placeholder.container():
        st.markdown('<div style="margin-top: 3.1rem;"></div>', unsafe_allow_html=True)
        st.markdown(f'##### Account: {st.session_state.user_id}')

    with st.container(border=True):
        st.header('Узнать погоду')
        city = st.text_input('Введите город', on_change=lambda: switch_view('search'))

        col_left, col_mid, col_right = st.columns([6.7, 1.5, 1.27])
        with col_mid:
            if st.button('Статистика'):
                switch_view('stats')
        with col_left:
            if st.button('Поиск'):
                switch_view('search')

        with col_right:
            if st.button('История'):
                switch_view('history')

    output_placeholder = st.empty()

    with output_placeholder.container():
        if st.session_state.current_view == 'stats':
            st.subheader('📊 Статистика')
            with st.spinner('Загрузка...'):
                response = httpx.get(f'{FASTAPI_URL}/stats/{st.session_state.user_id}')
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
                        y=alt.Y('count:Q', title='Количество'),
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
                            match int(str(city_info['count'])[-2::]):
                                case 12 | 13 | 14:
                                    st.write(f'- {city_info['city']}: {city_info['count']} раз')
                                case 2 | 3 | 4:
                                    st.write(f'- {city_info['city']}: {city_info['count']} раза')
                                case _:
                                    st.write(f'- {city_info['city']}: {city_info['count']} раз')
                        st.session_state.download_stats_show = True

                    if st.session_state.download_stats_show is True:
                        st.download_button(label='Нажмите, чтобы скачать статистику', data = data['stats'], file_name='stats.txt')
        elif st.session_state.current_view == 'search':
            st.subheader('🔎 Результат поиска')
            with st.container(border=True):
                if len(city) <= 0:
                    st.error('Поле ввода не должно быть пустым')
                else:
                    try:
                        with st.spinner('Загрузка...'):
                            data = httpx.get(f'{FASTAPI_URL}/weather/{city}').json()
                        weather = data['weather']
                        data = {
                            'user_id': st.session_state.user_id,
                            'city': city,
                            'weather': data['row']
                        }
                        httpx.post(f'{FASTAPI_URL}/history', json=data)
                        st.session_state.history_cleaned = False
                        st.success(weather)
                    except json.decoder.JSONDecodeError:
                        st.write('Не получилось отправить запрос. Попробуйте позже.')
                    except:
                        st.write('Произошла непредвиденная ошибка')
        elif st.session_state.current_view == 'history':
            st.subheader('📜 История запросов')
            with st.container(border=True):
                st.session_state.history_cleaned = False
                with st.spinner('Загрузка...'):
                    response = httpx.get(f'{FASTAPI_URL}/history/{st.session_state.user_id}')
        
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
                        response = httpx.delete(f'{FASTAPI_URL}/history/{st.session_state.user_id}')
                    switch_view()
                    st.session_state.history_cleaned = True
                    st.rerun()
            
    if st.session_state.history_cleaned:
        st.success('История очищена')