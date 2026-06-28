import altair as alt
import pandas as pd
import streamlit as st
import httpx
import json
from api_client import fetch_weather, fetch_history, fetch_stats, save_history, delete_history

def init_session_state():
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

    if 'search_forecast' not in st.session_state:
        st.session_state.search_forecast = 'now'
    
    if 'search_part' not in st.session_state:
        st.session_state.search_part = 'day'

def switch_view(to_view=None):
    st.session_state.current_view = to_view
    st.session_state.cleaner_show = False
    st.session_state.history_cleaned = False
    st.session_state.download_stats_show = False

def try_to_int(text: str) -> int | None:
    try:
        return int(text)
    except ValueError:
        return None

def render_search(city: str) -> None:
    def set_forecast(day):
        st.session_state.search_forecast = day
    
    def set_part(part):
        st.session_state.search_part = part
    

    col_now, col_today, col_tomorrow, col_void = st.columns([0.2, 0.2, 0.2, 0.4])
    with col_now:
        today_button = st.button('Сейчас', width='stretch', type="primary", on_click=set_forecast, args=('now',))
    with col_today:
        today_button = st.button('Сегодня', width='stretch', type="primary", on_click=set_forecast, args=('today',))
    with col_tomorrow:
        tomorrow_button = st.button('Завтра', width='stretch', type="primary", on_click=set_forecast, args=('tomorrow',))
    with st.container(border=True):
        col_morning, col_day, col_evening, col_night, col_void = st.columns([0.2, 0.2, 0.2, 0.2, 0.2])
        if st.session_state.search_forecast != 'now':
            with col_morning:
                morning_button = st.button('Утром', width='stretch', type="secondary", on_click=set_part, args=('morning',))
            with col_day:
                day_button = st.button('Днём', width='stretch', type="secondary", on_click=set_part, args=('day',))
            with col_evening:
                evening_button = st.button('Вечером', width='stretch', type="secondary", on_click=set_part, args=('evening',))
            with col_night:
                night_button = st.button('Ночью', width='stretch', type="secondary", on_click=set_part, args=('night',))

        try:
            with st.spinner('Загрузка...'):
                data = fetch_weather(city, st.session_state.search_forecast, st.session_state.search_part)
            weather = data['weather']

            save_history(st.session_state.user_id, city, data['row'])
            st.session_state.history_cleaned = False

            for criteria, criteria_data in weather.items():
                with st.container(border=True):
                    st.write(f'**{criteria}:** {criteria_data}')
        except json.decoder.JSONDecodeError:
            st.write('Не получилось отправить запрос. Попробуйте позже.')
        except (KeyError, httpx.ReadTimeout):
            st.error('Неверный запрос. Проверьте поле ввода.')

def render_stats(user_id: int) -> None:
    with st.spinner('Загрузка...'):
        data =  fetch_stats(user_id)

    if data['total_queries'] == 0:
        with st.container(border=True):
            st.write('Нет данных для статистики')
    else:
        top_cities = data['top_cities']
        
        with st.container(border=True):

            df = pd.DataFrame(top_cities)
            chart = alt.Chart(df).mark_bar().encode(
                x=alt.X('city:N', title='Город', sort='-y'),
                y=alt.Y('count:Q', title='Количество'),
                color=alt.Color('city', title='Всего', legend=None)
            ).properties(title='Топ городов по запросам',
            height=350
            ).configure_view(strokeWidth=0)
            
            st.altair_chart(chart)

        with st.container(border=True):
            st.write(f'**Всего запросов:** {data['total_queries']}')
            st.write(f'**Чаще всего вы искали погоду в:**')
            for city_info in data['top_cities']:
                count = city_info['count']
                city = city_info['city']
                match count % 100 if count % 100 in [12, 13, 14] else count % 10:
                    case 2 | 3 | 4:
                        word = 'раза'
                    case _:
                        word = 'раз'
                st.write(f'- {city}: {count} {word}')

            st.download_button(label='Нажмите, чтобы скачать статистику', data = data['stats'], file_name='stats.txt')

def render_history(user_id: int) -> None:
    with st.container(border=True): 
        st.session_state.history_cleaned = False
        with st.spinner('Загрузка...'):
            data =  fetch_history(user_id)

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
                delete_history(user_id)
            switch_view()
            st.session_state.history_cleaned = True
            st.rerun()

def main():
    
    init_session_state()

    st.set_page_config(page_title="Погода", page_icon="⛅")

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
            user_id = st.text_input(label='Ввод id', label_visibility='collapsed', max_chars=9)
            col_void, col_sign = st.columns([0.89, 0.11])
            with col_sign:
                if st.button('Войти', width='content'):
                    user_id = try_to_int(user_id)
                    if not user_id is None and user_id > 0:
                        st.session_state.user_id = user_id
                        st.session_state.sign_in_success = True
                        switch_view()
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
                switch_view()
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
                render_stats(st.session_state.user_id)
                
            elif st.session_state.current_view == 'search':
                if len(city) <= 0:
                    st.error('Поле ввода не должно быть пустым')
                elif not try_to_int(city) is None:
                    st.error('Название города не может состоять только из цифр.')
                else:
                    st.subheader('🔎 Результат поиска')
                    render_search(city)
    
            elif st.session_state.current_view == 'history':
                st.subheader('📜 История запросов')
                render_history(st.session_state.user_id)
                
        if st.session_state.history_cleaned:
            st.success('История очищена')

if __name__ == '__main__':
    main()