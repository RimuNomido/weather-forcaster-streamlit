import streamlit as st
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


st.title('⛅Погода')

with st.container(border=True):
    st.header('Узнать погоду')
    city = st.text_input('Введите город')

    col_left, col_mid, col_right = st.columns([6.7, 1.5, 1.27])
    with col_mid:
        stats_button = st.button('Статистика')

    with col_left:
        search_button = st.button('Поиск')

    with col_right:
        show_history_button = st.button('История')

    if 'cleaner_show' not in st.session_state:
        st.session_state.cleaner_show = False

    if 'history_cleaned' not in st.session_state:
        st.session_state.history_cleaned = False

    if stats_button:
        st.session_state.history_cleaned = False
        st.session_state.cleaner_show = False
        st.subheader('📊 Статистика')
        with st.container(border=True):
            response = httpx.get(f'{FASTAPI_URL}/stats/12345')
            data = response.json()
            top_cities = data['top_cities']

            if data['total_queries'] == 0:
                st.write('Нет запросов для статистики')
            else:
                st.write(f'**Всего запросов:** {data['total_queries']}')
                st.write(f'**Чаще всего вы искали погоду в:**')
                for city_info in data['top_cities']:
                    st.write(f'- {city_info['city']}: {city_info['count']} раз')
            st.download_button(label='Нажмите, чтобы скачать статистику', data = data['stats'], file_name='stats.txt')

    if search_button:
        st.subheader('🔎 Результат поиска')
        with st.container(border=True):
            if st.session_state.cleaner_show is True:
                st.session_state.cleaner_show = False
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
    
    if show_history_button:
        st.subheader('📜 История запросов')
        with st.container(border=True):
            st.session_state.history_cleaned = False
            with st.spinner('Загрузка...'):
                response = httpx.get(f'{FASTAPI_URL}/history/12345')
    
            data = response.json()
            if data['total'] == 0:
                st.write('История запросов пуста')
            else:
                st.write(data['history'])
                st.write('### Общее количество запросов: ', data['total'])
                st.session_state.cleaner_show = True
    
    if st.session_state.cleaner_show:
        clear_history_button = st.button('Очистить историю')
        if clear_history_button:
            with st.spinner('Загрузка...'):
                response = httpx.delete(f'{FASTAPI_URL}/history/12345')
            st.session_state.history_cleaned = True
            st.session_state.cleaner_show = False
            st.rerun()
    
    if st.session_state.history_cleaned:
        st.success('История очищена')