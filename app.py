import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'MS Gothic'       #グラフ用日本語フォント設定

#!^!==================== タイトルと紹介 =================!^!#

st.markdown("""
    <style>
    .block-container {
        background-color: #f3f3f3;
        padding: 20px;
        border-radius: 50px;
    }
    [data-testid="stSidebar"] {
        background-color: #e6e6e6;
    </style>
    """,
    unsafe_allow_html=True
)
# タイトルと説明文
st.markdown(
    """
    <h1 style="text-align: center; color: black;"><div style='color: red;'>死因別死亡確率</div>可視化アプリ</h1>
    <h3 style='color: black;'>死因別死亡確率とは？</h3>
    <p style='color: black;'>特定の死因による死亡数を同年齢層の総死亡数で割った割合を指します。
        この指標は、<u>特定の死因が各年齢層においてどれほどの影響を及ぼしているか</u>を理解するために用いられます。</p>
    <p style='color: black;'>データ出典: <a href='https://www.e-stat.go.jp' target='_blank'>e-Stat 政府統計の総合窓口</a></p>
    """,
    unsafe_allow_html=True
)

#!^!==================== データの読み込みと前処理 =================!^!#

# データの読み込み
df = pd.read_csv('00003.csv', encoding='shift_jis')

# 上書きしないデータ
df_all = pd.read_csv('00003.csv', encoding='shift_jis')

# フィルタリング
causes = df['死因'].unique()

#!^!==================== サイドバーのUI要素 =================!^!#

with st.sidebar:
    st.header('サイドバー')
    
    with st.expander('表及び折れ線グラフについての絞り込み'):
        # 死因の選択
        selected_cause = st.multiselect("死因を選択してください", causes)
        df = df[df['死因'].isin(selected_cause)]

        # 性別の選択
        selected_sex = st.selectbox("性別を選択してください", ['男性', '女性', '両方'])

        # もし男性と選択されたなら、'男性'列のみを残す
        if selected_sex == '男性':
            df = df[["死因"] + [col for col in df.columns if '男性' in col]]

        elif selected_sex == '女性':
            df = df[["死因"] + [col for col in df.columns if '女性' in col]]

        else:  # 男女両方
            df = df

    st.write('---')
    
    with st.expander('ランキング(棒グラフ)についての絞り込み'):
        selected_sex2 = st.selectbox('性別を選択してください（グラフ用）', ['男性', '女性'])
        selected_age = st.selectbox('年齢層を選択してください（グラフ用）', ['0歳', '20歳', '40歳', '65歳', '75歳', '90歳'])

target_column = f'{selected_sex2}{selected_age}'

#!^!==================== データの表示 =================!^!#

st.divider()
st.subheader('年齢層・性別ごとの死因別死亡確率データ')
st.caption('※サイドバーから表示する死因・性別を絞り込めます。')

if df.empty:
    st.info("サイドバーから死因を選択すると、ここにデータが表示されます。")
else :
    st.dataframe(df, height=500, width=950)

#!^!==================== 折れ線グラフの表示 =================!^!#

st.divider()
st.subheader('年齢による死因別死亡確率の変化')
st.caption('※サイドバーで絞り込んだデータのみを表示します。')
st.write('このグラフから、とある死因の死亡確率は年齢が上がるごとに'
         'どのように変化するかを確認することができます。')
# '死因'のデータをフィルタリング
#       ↳選択されていないときのError対策
filtered = df[df['死因'].isin(selected_cause)]

# 未選択時は、info表示してErrorを逃がす
if filtered.empty:
    st.info("サイドバーから死因を選択すると、ここに折れ線グラフが表示されます。")

else:
    # 年齢層のリスト
    ages = ['0歳', '20歳', '40歳', '65歳', '75歳', '90歳']

    # 折れ線グラフの描画
    fig, ax = plt.subplots(figsize=(14, 8))
    # 性別に応じた描画設定
    draw_male = selected_sex in ['男性', '両方']
    draw_female = selected_sex in ['女性', '両方']

    for _, row in filtered.iterrows():
        cause = row['死因']

        if draw_male:       # 男性データの描画
            male_cols = [f'男性{age}' for age in ages if f'男性{age}' in df.columns]
            if male_cols:
                ax.plot(
                    ages[:len(male_cols)],
                    row[male_cols],
                    marker='o',
                    label=f'{cause}（男性）'
                )

        if draw_female:     # 女性データの描画
            female_cols = [f'女性{age}' for age in ages if f'女性{age}' in df.columns]
            if female_cols:
                ax.plot(
                    ages[:len(female_cols)],
                    row[female_cols],
                    marker='o',
                    linestyle='--',
                    label=f'{cause}（女性）'
                )

    ax.set_xlabel("年齢")
    ax.set_ylabel("死亡確率(%)")
    ax.legend(
    bbox_to_anchor=(1.02, 1),
    loc='upper left',
    borderaxespad=0,
    fontsize=10
    )

    st.pyplot(fig)

#!^!==================== 棒グラフの表示 =================!^!

st.divider()
st.subheader(f'{selected_sex2}{selected_age} | 死因別死亡確率ランキング')
st.caption('※サイドバーで選択した死因の中から、' \
         f'{selected_sex2}{selected_age}の死亡確率が高い順に表示します。')
st.write('このグラフから、特定の年齢層においてどの死因がより深刻な影響を及ぼしているかを確認できます。')

# ここで、上書きされていない「df_all」のデータを使用することで
# 表・折れ線グラフで選択されていない性別を選択していたとしても
# エラーなしで参照できる
filtered2 = df_all[df_all['死因'].isin(selected_cause)][['死因', target_column]]

# 未選択時は、info表示してErrorを逃がす
if filtered2.empty:
    st.info("サイドバーから死因を選択すると、ここに棒グラフが表示されます。")

else :
    ranking = filtered2.sort_values(by=target_column, ascending=False)

    fig2, ax2 = plt.subplots(figsize=(14, 10))

    ax2.barh(
    ranking['死因'],
    ranking[target_column],
    color='skyblue'
    )

    # 棒グラフの各バーに値を表示
    for i, v in enumerate(ranking[target_column]):
        ax2.text(v + 0.1, i, f"{v:.2f}%", va='center', ha='left', fontsize=9)

    ax2.invert_yaxis()  # 大きい値を上に表示
    ax2.set_xlabel("死亡確率(%)")
    st.pyplot(fig2)