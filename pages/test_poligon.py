import streamlit as st
import geemap.foliumap as geemap
import pandas as pd

# Title of the Streamlit app
st.title("Bekzhan's Interactive Map")

# A simple select box with test values
a = ['1', '2', '3', '4']
st.selectbox('Select a value', a)

# Creating two columns with a 4:1 ratio
col1, col2 = st.columns([4, 1])

# Getting the list of available basemaps and finding the index for OpenTopoMap
options = list(geemap.basemaps.keys())
index = options.index("OpenTopoMap")

# Select box for choosing a basemap, placed in the smaller column (col2)
with col2:
    basemap = st.selectbox("Select a basemap:", options, index)

# Map display in the larger column (col1)
with col1:
    m = geemap.Map()
    m.add_basemap(basemap)
    m.to_streamlit(height=700)

# File uploader for Excel files
uploaded_file = st.sidebar.file_uploader("Excel", type=["xlsx"])
st.color_picker()
#
# # Создание вкладки "Загрузка Excel-файла"
# if uploaded_file is not None:
#     # Чтение данных из Excel-файла
#     xls = pd.ExcelFile(uploaded_file)
#
#     # Выбор листа из файла Excel
#     sheet_name = st.sidebar.selectbox("Выберите лист", xls.sheet_names)
#
#     # Предполагаем, что данные находятся на выбранном листе
#     df = xls.parse(sheet_name)

    # # Удаление столбца с именем "Год" (замените его на имя вашего столбца)
    # if "Год" in df.columns:
    #     df = df.drop(columns=["Год"])

    # # Создание графика на основе данных (первый график - точечная диаграмма)
    # x_col = st.sidebar.selectbox("Столбец для оси X", df.columns)
    # y_col = st.sidebar.selectbox("Столбец для оси Y", df.columns)
    #
    # # Перенесено в этот блок
    # st.write(f"### График: {x_col} по отношению к {y_col}")
    #
    # fig, ax = plt.subplots(figsize=(10, 6))
    # ax.plot(df[x_col], df[y_col], marker='o')  # Используйте plt.plot для линейной диаграммы с точками
    # ax.set_xlabel(x_col)
    # ax.set_ylabel(y_col)
    # st.pyplot(fig)

  # # Кнопка для выполнения анализа данных на основе графика
  #   if st.button("Выполнить анализ данных"):
  #       st.write("### Результаты анализа данных")
  #
  #       # Пример анализа данных с использованием библиотеки seaborn
  #       sns.pairplot(df[[x_col, y_col]])
  #       st.pyplot()