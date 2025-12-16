import joblib
import numpy as np
import streamlit as st
import pandas as pd
import random
import time
import hashlib


import psycopg2
import pandas as pd
from datetime import datetime
import streamlit as st

# --- НАСТРОЙКИ ПОДКЛЮЧЕНИЯ (НОВЫЙ СПОСОБ - ЧЕРЕЗ ССЫЛКУ) ---
# Вставьте сюда строку, которую скопировали, и ВПИШИТЕ ПАРОЛЬ вместо [YOUR-PASSWORD]
DATABASE_URL = "postgresql://postgres.ohxmtufigupkmndhznin:Halamadrid2025@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres"

# 1. Функция подключения
def get_connection():
 # Мы передаем ссылку целиком, библиотека сама разберется
 return psycopg2.connect(DATABASE_URL, sslmode='require')

# ... (Ваш код подключения и функции student_interface/curator_interface остаются выше) ...



# 2. Создание таблицы в облаке (запустится один раз)
def init_db():
 try:
  conn = get_connection()
  cur = conn.cursor()
  cur.execute('''
   CREATE TABLE IF NOT EXISTS student_data (
    id SERIAL PRIMARY KEY,
    timestamp TEXT,
    student_name TEXT,
    curator_name TEXT,
    uni TEXT,
    course INTEGER,
    specialty TEXT,
    bmi REAL,
    stress INTEGER,
    status TEXT,
    gender TEXT,
    age INTEGER,
    height INTEGER,
    weight INTEGER,
    sys_bp INTEGER,
    dia_bp INTEGER,
    pulse INTEGER,
    sleep_dur REAL,
    sleep_qual INTEGER,
    phys_activity INTEGER,
    steps INTEGER,
    ai_verdict TEXT
   );
  ''')
  cur.execute('''
   CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL
   );
  ''')
  conn.commit()
  cur.close()
  conn.close()
  print("✅ Таблица в Supabase успешно проверена/создана!")
 except Exception as e:
  st.error(f"Ошибка подключения к базе данных: {e}")

# 3. Сохранение данных в облако
def save_student_form(data_dict):
 conn = get_connection()
 cur = conn.cursor()
 
 data_dict['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
 cur.execute('''
  INSERT INTO student_data 
  (timestamp, student_name, curator_name, uni, course, specialty, bmi, stress, status,
  gender, age, height, weight, sys_bp, dia_bp, pulse, sleep_dur, sleep_qual, phys_activity, steps, ai_verdict)
  VALUES (%(timestamp)s, %(name)s, %(curator)s, %(uni)s, %(course)s, %(spec)s, %(bmi)s, %(stress)s, %(status)s,
    %(gender)s, %(age)s, %(height)s, %(weight)s, %(sys_bp)s, %(dia_bp)s, %(pulse)s, %(sleep_dur)s, %(sleep_qual)s, %(phys)s, %(steps)s, %(verdict)s)
 ''', data_dict)
 
 conn.commit()
 cur.close()
 conn.close()

# 4. Получение данных из облака
def get_all_data(curator_name=None, student_name=None):
 conn = get_connection()
 
 query = "SELECT * FROM student_data"
 params = None
 
 if curator_name:
  query += " WHERE curator_name = %s"
  params = (curator_name,)
 elif student_name:
  query += " WHERE student_name = %s"
  params = (student_name,)
 
 df = pd.read_sql_query(query, conn, params=params)
 conn.close()
 
 if not df.empty:
    df = df.rename(columns={
    "timestamp": "Дата/Время",
    "student_name": "ФИО",
    "uni": "Uni",
    "course": "Курс",
    "specialty": "Специальность",  
         "bmi": "BMI",
   "stress": "Stress",
   "status": "Status"
  })
    df = df.sort_values(by="Дата/Время", ascending=False)
  
 return df





# ==========================================
# ВСТАВИТЬ ЭТО ПЕРЕД chcek_login или main
# ==========================================





# ==========================================

# Запуск


# Запуск инициализации при старте
init_db()





# --- Настройки страницы ---
st.set_page_config(
    page_title="Health System KZ",
    page_icon="🏥",
    layout="wide"
)

# --- Инициализация состояния ---
if 'language' not in st.session_state:
    st.session_state['language'] = 'Қазақша'
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_role' not in st.session_state:
    st.session_state['user_role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = ""

def set_language(lang):
    st.session_state['language'] = lang

# --- СЛОВАРЬ ПЕРЕВОДОВ ---
translations = {
    "Қазақша": {
        # Общее
        "login_title": "Жүйеге кіру",
        "login_subtitle": "Авторизациядан өтіңіз",
        "role_label": "Кім болып кіресіз?",
        "role_student": "Студент",
        "role_curator": "Куратор",
        "login_btn": "Кіру",
        "logout": "Шығу",
        
        # Студент - Личные
        "st_title": "Денсаулықты бағалау",
        "st_instr": "Деректерді толтырыңыз:",
        "full_name": "Аты-жөні (ФИО)",
        "uni_label": "Университет",
        "curator_label": "Куратор",
        "personal_header": "Антропометриялық деректер",
        "gender": "Жынысы",
        "age": "Жасы",
        "height": "Бойы (см)",
        "weight": "Салмағы (кг)",
        
        # Студент - Мед
        "med_header": "Медициналық көрсеткіштер",
        "sys_bp": "Жоғарғы қан қысымы (120)",
        "dia_bp": "Төменгі қан қысымы (80)",
        "pulse": "Тамыр соғысы (Пульс)",
        
        # Студент - Образ жизни
        "life_header": "Өмір салты",
        "sleep": "Тәуліктік ұйқы (сағат)",
        "stress": "Күйзеліс деңгейі (0-10)",
        
        # Результаты
        "calc_btn": "Талдау жасау",
        "result_title": "Диагностика нәтижесі",
        "bmi": "ДСИ (Индекс)",
        "bp": "Қан қысымы",
        "advice_header": "Жүйенің ұсыныстары:",
        
        # Куратор
        "cur_title": "Куратор панелі",
        "cur_subtitle": "Тіркелген студенттер мониторингі",
        "filter_risk": "Тек қауіп тобын көрсету (Risk)",
        "total_st": "Барлық студенттер:",
        "risk_st": "Қауіп тобында:",
        
        # Статусы
        "status_norm": "Қалыпты",
        "status_warning": "Назар аударыңыз",
        "status_risk": "Қауіпті (Risk)",
        "reg_title": "Тіркелу",
        "login_tab": "Кіру",
        "reg_tab": "Тіркелу",
        "reg_btn": "Тіркелу",
        "auth_error": "Қате логин немесе пароль",
        "reg_success": "Тіркелу сәтті өтті! Енді кіріңіз.",
        "reg_exists": "Бұл логин бос емес.",


        
    },
    "Русский": {
        # Общее
        "login_title": "Вход в систему",
        "login_subtitle": "Пожалуйста, авторизуйтесь",
        "role_label": "Выберите роль",
        "role_student": "Студент",
        "role_curator": "Куратор",
        "login_btn": "Войти",
        "logout": "Выйти",
        
        # Студент - Личные
        "st_title": "Оценка здоровья",
        "st_instr": "Заполните данные для анализа:",
        "full_name": "ФИО студента",
        "uni_label": "Университет",
        "curator_label": "Куратор",
        "personal_header": "Антропометрические данные",
        "gender": "Пол",
        "age": "Возраст",
        "height": "Рост (см)",
        "weight": "Вес (кг)",
        
        # Студент - Мед
        "med_header": "Медицинаские показатели",
        "sys_bp": "Верхнее давление (120)",
        "dia_bp": "Нижнее давление (80)",
        "pulse": "Пульс (уд/мин)",
        
        # Студент - Образ жизни
        "life_header": "Образ жизни",
        "sleep": "Сон (часов в сутки)",
        "stress": "Уровень стресса (0-10)",
        
        # Результаты
        "calc_btn": "Получить анализ",
        "result_title": "Результаты диагностики",
        "bmi": "ИМТ (Индекс)",
        "bp": "Давление",
        "advice_header": "Рекомендации системы:",
        
        # Куратор
        "cur_title": "Панель куратора",
        "cur_subtitle": "Мониторинг прикрепленных студентов",
        "filter_risk": "Показать только группу риска",
        "total_st": "Всего студентов:",
        "risk_st": "В группе риска:",
        
        # Статусы
        "status_norm": "Норма",
        "status_warning": "Требует внимания",
        "status_risk": "Риск (Risk)",
        "reg_title": "Регистрация",
        "login_tab": "Вход",
        "reg_tab": "Регистрация",
        "reg_btn": "Зарегистрироваться",
        "auth_error": "Неверный логин или пароль",
        "reg_success": "Регистрация успешна! Теперь войдите.",
        "reg_exists": "Такой пользователь уже существует.",
    }
}

current_lang = st.session_state['language']
t = translations[current_lang]
uni_list = ["KazNU", "KBTU", "Satbayev University", "Narxoz", "ATU"]

# --- ЛОГИКА АНАЛИЗА (ДЛЯ СТУДЕНТА) ---
def analyze_health_logic(height, weight, sys_bp, dia_bp, pulse, sleep, stress, lang_code):
    recs = []
    status = t["status_norm"]
    color = "success"
    
    # ИМТ
    bmi = round(weight / ((height/100)**2), 2)
    
    # Тексты ошибок
    if lang_code == "Қазақша":
        txt_bmi = f"ДСИ {bmi}: Салмақ нормада емес."
        txt_bp = "Қан қысымы жоғары! Дәрігерге қаралыңыз."
        txt_pulse = "Тахикардия (Жоғары пульс)."
        txt_sleep = "Ұйқының созылмалы жетіспеушілігі."
        txt_stress = "Өте жоғары күйзеліс деңгейі."
        txt_ok = "Көрсеткіштер қалыпты!"
    else:
        txt_bmi = f"ИМТ {bmi}: Отклонение веса от нормы."
        txt_bp = "Высокое давление! Обратитесь к врачу."
        txt_pulse = "Тахикардия (Высокий пульс)."
        txt_sleep = "Хронический недосып."
        txt_stress = "Критический уровень стресса."
        txt_ok = "Показатели в норме!"

    # Проверки
    if bmi < 18.5 or bmi > 25:
        recs.append(txt_bmi)
        status = t["status_warning"]
        color = "warning"
    
    if sys_bp > 130 or dia_bp > 85:
        recs.append(txt_bp)
        status = t["status_risk"]
        color = "error"

    if pulse > 100:
        recs.append(txt_pulse)
        if status != t["status_risk"]: status = t["status_warning"]

    if sleep < 6:
        recs.append(txt_sleep)
    
    if stress > 8:
        recs.append(txt_stress)
        
    if not recs:
        recs.append(txt_ok)
        
    return status, color, recs, bmi

# --- СИМУЛЯЦИЯ ДАННЫХ (ДЛЯ КУРАТОРА) ---
# Измененная функция генерации данных
def get_data_for_specific_students(student_names):
    if not student_names:
        return pd.DataFrame(columns=["ID", "ФИО", "Uni", "BMI", "Stress", "Status"])

    data = []
    for i, name in enumerate(student_names):
        
        # --- МАГИЯ ЗДЕСЬ ---
        # Мы закрепляем генератор случайных чисел за конкретным именем.
        # Теперь для "Ivanov" всегда выпадут одни и те же числа,
        # даже если перезагрузить страницу.
        random.seed(name) 
        # -------------------

        uni = random.choice(uni_list) if 'uni_list' in globals() else "Unknown Uni"
        bmi = round(random.uniform(18.0, 32.0), 1)
        stress = random.randint(3, 10)
        
        st_val = "Norm"
        if bmi > 26 or stress > 8:
            st_val = "Risk ⚠️"
        elif bmi > 25:
            st_val = "Warning"
            
        data.append({
            "ID": i+1,
            "ФИО": name,
            "Uni": uni,
            "BMI": bmi,
            "Stress": stress,
            "Status": st_val
        })
    
    # Сбрасываем seed, чтобы другие части программы (если есть) были реально случайными
    random.seed(None) 
    
    return pd.DataFrame(data)

# --- ИНТЕРФЕЙС СТУДЕНТА (ПОЛНЫЙ) ---
# --- ЗАГРУЗКА МОДЕЛИ (Вставьте это перед функцией student_interface) ---
try:
    # Пытаемся загрузить обученную модель
    ml_model = joblib.load('sleep_model.pkl')
    model_loaded = True
    print("✅ Модель ML успешно загружена!")
except Exception as e:
    model_loaded = False
    print(f"⚠️ Ошибка загрузки модели: {e}")
  


# --- ИНТЕРФЕЙС СТУДЕНТА ---
# --- ИНТЕРФЕЙС СТУДЕНТА (ПОЛНЫЙ И ИСПРАВЛЕННЫЙ) ---
def student_interface():
    st.title(f"👤 {t['st_title']}")
    st.write(t['st_instr'])
    st.divider()
    
    # 1. Личные данные (Верхний блок)
    col_u1, col_u2, col_u3, col_u4 = st.columns([2, 1, 1, 1])
    with col_u1:
        name_val = st.text_input(t['full_name'], value=st.session_state['username'], disabled=True)
    with col_u2:
        uni_val = st.selectbox(t['uni_label'], uni_list)
    with col_u3:
        course_val = st.selectbox("Курс", [1, 2, 3, 4])
    with col_u4:
        # Ваш список специальностей
        specs = ["IT", "Medicine", "Engineering", "Economy", "Law"] 
        spec_val = st.selectbox("Спец-ть", specs)
    
    curator_val = st.text_input(t.get('curator_label', 'Куратор'))
    st.divider()

    # 2. Ввод данных для ИИ (11 параметров)
    st.subheader("📊 Данные для ИИ-анализа")
    st.info("Заполните все поля, чтобы искусственный интеллект мог оценить риски.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Пол (нужен для модели)
        gender_str = st.selectbox(t['gender'], ["Man/Ер", "Woman/Әйел"])
        
        # Возраст
        age = st.number_input(t['age'], 16, 60, 20)
        
        # Рост и Вес (для BMI)
        height = st.number_input(t['height'], 100, 230, 175)
        weight = st.number_input(t['weight'], 40, 160, 70)
        
        # НОВЫЕ ПОЛЯ (Нужны для вашей модели!)
        phys_activity = st.slider("Физ. активность (мин/день)", 0, 120, 45, help="Сколько минут в день вы активно двигаетесь?")
        steps = st.number_input("Шагов в день", 0, 30000, 6000, step=500)

    with col2:
        sys_bp = st.number_input(t['sys_bp'], 80, 200, 120)
        dia_bp = st.number_input(t['dia_bp'], 50, 130, 80)
        
        # --- БЛОК IOT: ВЫБОР ИСТОЧНИКА ПУЛЬСА ---
        st.write("❤️ **Пульс (Heart Rate)**")
        pulse_mode = st.radio("Источник данных:", ["Вручную / Manual", "С датчика (IoT)"], horizontal=True, label_visibility="collapsed")
        
        if "Вручную" in pulse_mode:
            # Обычный ввод
            pulse = st.number_input("Введите пульс", 40, 180, 72, label_visibility="collapsed")
        else:
            # === РЕЖИМ РАБОТЫ С ДАТЧИКОМ ===
            st.info("Режим работы с оборудованием")
            
            col_iot1, col_iot2 = st.columns([1, 1])
            
            # 1. Кнопка одиночного замера
            with col_iot1:
                if st.button("🔄 Взять пульс"):
                    try:
                        response = supabase.table("live_pulse").select("*").order("created_at", desc=True).limit(1).execute()
                        if response.data:
                            sensor_val = response.data[0]['pulse']
                            st.session_state['sensor_pulse'] = sensor_val
                            st.toast(f"Получено: {sensor_val}", icon="❤️")
                    except:
                        st.error("Ошибка связи")
            
            # 2. Чекбокс для графика
            with col_iot2:
                live_mode = st.checkbox("📈 Живой график")

            # Отображение цифры
            pulse = st.session_state.get('sensor_pulse', 72)
            st.metric("Значение пульса:", f"{pulse} уд/мин")

            # 3. Логика отрисовки графика (Только если нажата галочка)
            if live_mode:
                st.caption("График обновляется каждые 2 секунды...")
                
                try:
                    # Скачиваем последние 20 точек
                    resp = supabase.table("live_pulse").select("created_at, pulse").order("created_at", desc=True).limit(20).execute()
                    
                    if resp.data:
                        df_pulse = pd.DataFrame(resp.data)
                        # Сортируем по времени (слева направо)
                        df_pulse = df_pulse.sort_values(by="created_at")
                        
                        # Рисуем
                        st.line_chart(df_pulse.set_index("created_at")["pulse"])
                        
                        # Пауза и перезагрузка страницы для эффекта "Live"
                        time.sleep(2)
                        st.rerun()
                    else:
                        st.warning("База данных пуста.")
                except Exception as e:
                    st.error(f"Ошибка графика: {e}")
        
        # ------------------------------------------

        sleep_dur = st.slider(t['sleep'], 4.0, 12.0, 7.0, 0.5)
        sleep_qual = st.slider("Качество сна (1-10)", 1, 10, 6)
        stress = st.slider(t['stress'], 1, 10, 5)

    # --- ВАЖНО: РАСЧЕТ BMI ДОЛЖЕН БЫТЬ ЗДЕСЬ (ПЕРЕД КНОПКОЙ) ---
    bmi_val = round(weight / ((height / 100) ** 2), 2)
    st.caption(f"Ваш BMI: {bmi_val}")
    st.divider()

    # --- ГЛАВНАЯ КНОПКА ---
    if st.button("🧠 Запустить анализ (AI)", type="primary"):
        
        # А. Подготовка данных для модели
        # 1. Кодируем пол (Man=1, Woman=0 - как при обучении)
        gender_code = 1 if "Man" in gender_str or "Ер" in gender_str else 0
        
        # 2. Кодируем BMI. ТЕПЕРЬ bmi_val ТОЧНО СУЩЕСТВУЕТ
        if bmi_val < 25: bmi_code = 0
        elif bmi_val < 30: bmi_code = 1
        else: bmi_code = 2

        # Б. ПРЕДСКАЗАНИЕ
        ai_verdict = "Неизвестно"
        final_color = "info"
        
        if model_loaded:
            # СТРОГИЙ ПОРЯДОК:
            features = np.array([[
                age, 
                sleep_dur, 
                sleep_qual, 
                phys_activity, 
                stress, 
                pulse, 
                steps, 
                sys_bp, 
                dia_bp, 
                gender_code, 
                bmi_code
            ]])
            
            prediction = ml_model.predict(features)[0]
            
            # --- БЛОК 1: Базовый вердикт ИИ ---
            if prediction == 'None' or prediction == 'Healthy':
                ai_verdict = "Здоров (Healthy) ✅"
                final_color = "success"
            elif prediction == 'Insomnia':
                ai_verdict = "Риск: Бессонница (Insomnia) ⚠️"
                final_color = "warning"
            elif prediction == 'Sleep Apnea':
                ai_verdict = "Риск: Апноэ сна (Apnea) ❗"
                final_color = "error"
            else:
                ai_verdict = str(prediction)
                final_color = "info"

            # --- БЛОК 2: ГИБРИДНАЯ КОРРЕКЦИЯ (Safety Layer) ---
            check_messages = []
            
            if stress >= 8 and final_color == "success":
                ai_verdict = "Риск: Высокий уровень стресса (скрытая угроза) ⚠️"
                final_color = "warning"
                check_messages.append("Несмотря на хорошие физические показатели, уровень стресса критический.")

            if sleep_qual <= 3 and final_color == "success":
                ai_verdict = "Риск: Низкое качество сна ⚠️"
                final_color = "warning"
                check_messages.append("Ваше качество сна вызывает опасения.")

            if bmi_val > 30 and final_color == "success":
                check_messages.append("Обратите внимание на вес, это фактор риска для Апноэ.")

        else:
            st.error("Ошибка модели...")
            
        # В. Сохранение в базу
        if curator_val:
            full_data = {
                'name': name_val,
                'curator': curator_val,
                'uni': uni_val,
                'course': course_val,
                'spec': spec_val,
                'bmi': bmi_val,
                'stress': stress,
                'status': final_color,
                'gender': gender_str,
                'age': age,
                'height': height,
                'weight': weight,
                'sys_bp': sys_bp,
                'dia_bp': dia_bp,
                'pulse': pulse,
                'sleep_dur': sleep_dur,
                'sleep_qual': sleep_qual,
                'phys': phys_activity,
                'steps': steps,
                'verdict': ai_verdict
            }
            
            save_student_form(full_data)
            st.toast(f"Полная медкарта отправлена куратору {curator_val}!", icon="✅")
        else:
            st.warning("Куратор не указан — данные не сохранены.")
        
        # --- ОТОБРАЖЕНИЕ РЕЗУЛЬТАТОВ ---
        st.divider()
        st.subheader("Результат диагностики ИИ:")
        
        if final_color == "success":
            st.success(f"## {ai_verdict}")
            st.balloons()
        elif final_color == "warning":
            st.warning(f"## {ai_verdict}")
        else:
            st.error(f"## {ai_verdict}")
            
        if check_messages:
            for msg in check_messages:
                st.info(f"ℹ️ {msg}")
        
        # --- БЛОК ИСТОРИИ ---
        st.divider()
        st.subheader("📜 История ваших проверок")
        
        my_history_df = get_all_data(student_name=st.session_state['username'])
        
        if not my_history_df.empty:
            cols_to_show = ["Дата/Время", "ai_verdict", "BMI", "Stress", "sleep_qual", "steps"]
            available_cols = [c for c in cols_to_show if c in my_history_df.columns]
            
            st.dataframe(my_history_df[available_cols], use_container_width=True)
            st.line_chart(my_history_df.set_index("Дата/Время")["Stress"])
        else:
            st.info("История пуста. Пройдите первый анализ.")


# --- ИНТЕРФЕЙС КУРАТОРА ---
def curator_interface():
    current_curator = st.session_state.get("username", "Unknown")
    st.header(f"🎓 Кабинет куратора: {current_curator}")
    
    # 1. Загружаем ВСЮ историю всех студентов этого куратора
    df_all = get_all_data(curator_name=current_curator)
    
    if not df_all.empty:
        # --- ФИЛЬТРАЦИЯ: ОСТАВЛЯЕМ ТОЛЬКО ПОСЛЕДНЕЕ ---
        # Сортируем по времени (новые сверху) и удаляем дубликаты по ФИО, оставляя первое (т.е. новое)
        df_latest = df_all.sort_values(by="Дата/Время", ascending=False).drop_duplicates(subset=["ФИО"], keep="first")
        
        st.subheader(f"📋 Актуальный статус студентов ({len(df_latest)})")
        
        # Фильтры
        c1, c2 = st.columns(2)
        with c1:
            sel_course = st.multiselect("Курс", df_latest["Курс"].unique(), default=df_latest["Курс"].unique())
        with c2:
            sel_spec = st.multiselect("Специальность", df_latest["Специальность"].unique(), default=df_latest["Специальность"].unique())
            
        df_view = df_latest[(df_latest["Курс"].isin(sel_course)) & (df_latest["Специальность"].isin(sel_spec))]
        
        # Таблица (Основные данные)
        main_cols = ["ФИО", "Дата/Время", "Uni", "Курс", "Status", "ai_verdict"]
        st.dataframe(df_view[main_cols], hide_index=True)
        
        st.divider()

        # --- БЛОК ДЕТАЛЕЙ (Смотрим полную карточку) ---
        st.subheader("🔍 Подробный анализ")
        
        student_names = df_view["ФИО"].tolist()
        selected_student = st.selectbox("Выберите студента:", student_names)
        
        if st.button(f"Открыть карту: {selected_student}", type="primary"):
            # Берем данные конкретного студента из списка "последних"
            student_data = df_view[df_view["ФИО"] == selected_student].iloc[0]
            
            st.markdown(f"### 👤 {student_data['ФИО']} (Данные от: {student_data['Дата/Время']})")
            
            # ... (Тут ваш код вывода красивых колонок с данными) ...
            col_d1, col_d2, col_d3 = st.columns(3)
            with col_d1:
                st.markdown("#### ❤️ Сердце")
                st.write(f"**Давление:** {student_data.get('sys_bp')}/{student_data.get('dia_bp')}")
                st.write(f"**Пульс:** {student_data.get('pulse')}")
            with col_d2:
                st.markdown("#### 🏃 Тело")
                st.write(f"**Шаги:** {student_data.get('steps')}")
                st.write(f"**BMI:** {student_data['BMI']}")
            with col_d3:
                st.markdown("#### 🧠 Психология")
                st.write(f"**Стресс:** {student_data['Stress']}/10")
                st.write(f"**Сон:** {student_data.get('sleep_dur')}ч")
            
            # --- БОНУС: Кнопка "Посмотреть историю студента" для куратора ---
            with st.expander(f"Посмотреть историю изменений {selected_student}"):
                # Фильтруем общую таблицу только по этому студенту
                history_df = df_all[df_all["ФИО"] == selected_student]
                st.dataframe(history_df[["Дата/Время", "Stress", "sleep_qual", "steps", "ai_verdict"]])
                st.line_chart(history_df.set_index("Дата/Время")["Stress"])

    else:
        st.info("У вас пока нет данных от студентов.")



# --- НОВЫЕ ФУНКЦИИ ДЛЯ АВТОРИЗАЦИИ ---

def make_hash(password):
    """Шифрует пароль"""
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    """Проверяет пароль"""
    if make_hash(password) == hashed_text:
        return True
    return False

def add_user(username, password, role):
    """Регистрация нового пользователя в Supabase"""
    try:
        conn = get_connection()
        cur = conn.cursor()
        hashed_pass = make_hash(password)
        
        cur.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)', 
                    (username, hashed_pass, role))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        # Скорее всего такой юзер уже есть
        return False

def login_user(username, password):
    """Проверка входа через Supabase"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT password, role FROM users WHERE username = %s', (username,))
    data = cur.fetchone()
    
    conn.close()
    
    if data:
        stored_password, role = data
        if check_hashes(password, stored_password):
            return role
    return None
  

# --- СТРАНИЦА ЛОГИНА ---
# --- СТРАНИЦА ЛОГИНА (ОБНОВЛЕННАЯ) ---
def login_page():
    c1, c2, c3 = st.columns([8, 1, 1])
    with c2: 
        if st.button("🇰🇿"): set_language('Қазақша'); st.rerun()
    with c3:
        if st.button("🇷🇺"): set_language('Русский'); st.rerun()

    st.title("🏥 Health System KZ")
    
    # Создаем вкладки: Вход и Регистрация
    tab1, tab2 = st.tabs([t.get('login_tab', 'Login'), t.get('reg_tab', 'Register')])

    # --- Вкладка 1: ВХОД ---
    with tab1:
        st.subheader(t['login_title'])
        user = st.text_input("Login (Name)", key="l_user")
        pas = st.text_input("Password", type="password", key="l_pass")
        
        if st.button(t['login_btn']):
            # Проверяем через Supabase
            role = login_user(user, pas)
            if role:
                st.session_state['logged_in'] = True
                st.session_state['user_role'] = role
                st.session_state['username'] = user
                st.rerun()
            else:
                st.error(t.get('auth_error', 'Error'))

    # --- Вкладка 2: РЕГИСТРАЦИЯ ---
    with tab2:
        st.subheader(t.get('reg_title', 'Registration'))
        # Выбор роли при регистрации
        new_role = st.radio(t['role_label'], [t['role_student'], t['role_curator']], key="r_role")
        new_user = st.text_input("New Login", key="r_user")
        new_pas = st.text_input("New Password", type="password", key="r_pass")
        
        if st.button(t.get('reg_btn', 'Register')):
            if len(new_user) > 0 and len(new_pas) > 0:
                # Сохраняем в Supabase
                success = add_user(new_user, new_pas, new_role)
                if success:
                    st.success(t.get('reg_success', 'Success!'))
                else:
                    st.error(t.get('reg_exists', 'User exists'))
            else:
                st.warning("Введите логин и пароль")

# --- MAIN ---
if not st.session_state['logged_in']:
    login_page()
else:
    # Сайдбар
    with st.sidebar:
        st.title(st.session_state['username'])
        st.caption(f"Role: {st.session_state['user_role']}")
        
        if st.button(t['logout']):
            st.session_state['logged_in'] = False
            st.session_state['user_role'] = None
            st.rerun()
            
        st.divider()
        lang_now = st.radio("Language", ["Қазақша", "Русский"])
        if lang_now != st.session_state['language']:
            set_language(lang_now)
            st.rerun()

    # Роутер
    if st.session_state['user_role'] == t['role_student']:
        student_interface()
    elif st.session_state['user_role'] == t['role_curator']:

        curator_interface()





