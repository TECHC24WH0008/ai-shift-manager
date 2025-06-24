import streamlit as st
import pandas as pd

def load_input(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    elif file.name.endswith('.xlsx'):
        return pd.read_excel(file)
    else:
        st.error("対応しているのは .csv または .xlsx です。")
        return None

def simple_shift_allocation(df):
    if '名前' not in df.columns or '日付' not in df.columns:
        st.error("入力ファイルに「名前」と「日付」列が必要です。")
        return None
    df_result = df.copy()
    df_result['割当シフト'] = df_result['日付'] + " 17:00-21:00"
    return df_result

st.title("AIシフトマネージャー（簡易版）")

uploaded_file = st.file_uploader("勤務希望のCSVまたはExcelファイルをアップロード", type=['csv', 'xlsx'])

if uploaded_file is not None:
    df_input = load_input(uploaded_file)
    if df_input is not None:
        st.write("アップロードされた勤務希望表:")
        st.dataframe(df_input)

        if st.button("シフトを自動生成"):
            df_shift = simple_shift_allocation(df_input)
            if df_shift is not None:
                st.write("生成されたシフト表:")
                st.dataframe(df_shift)

                csv = df_shift.to_csv(index=False).encode('utf-8')
                st.download_button("CSVでダウンロード", data=csv, file_name='shift_result.csv', mime='text/csv')

                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df_shift.to_excel(writer, index=False, sheet_name='Shift')
                    writer.save()
                st.download_button("Excelでダウンロード", data=output.getvalue(), file_name='shift_result.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
