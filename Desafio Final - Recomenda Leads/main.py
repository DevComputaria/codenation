import streamlit as st
import altair as alt
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import squarify as sqy
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import base64
import warnings
warnings.simplefilter(action = 'ignore')

########## download ##########
def get_table_download_link(df, texto):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}" download="leads.csv">'+texto+'</a>'
    return href
########## download ##########

########## main ##########
def main():
    #st.image('img/codenationTD.png',format='PNG')
    st.title('AceleraDev Data Science 2020')
    st.subheader('**Recommend leads**')
########## sidebar ##########
    st.sidebar.header("Recomendação de Leads")
    tela = st.sidebar.radio("Selecione uma opção", options=["Exemplo com 3 Portfólios", "Gere Leads com seu Portfólio"], index=0)
    st.sidebar.markdown('Desenvolvido por: **Tiago Dias**')
    st.sidebar.markdown('Email para contato:')
    st.sidebar.markdown('diasctiago@gmail.com')
    st.sidebar.markdown('LinkedIn:')
    st.sidebar.markdown('https://www.linkedin.com/in/diasctiago')
    st.sidebar.markdown('GitHub:')
    st.sidebar.markdown('https://github.com/diasctiago')
########## sidebar ##########

########## Leitura dos dados ##########
    m1 = pd.read_csv('data/market1.csv')
    m2 = pd.read_csv('data/market2.csv')
    m3 = pd.read_csv('data/market3.csv')
    m4 = pd.read_csv('data/market4.csv')
    df = m1.append(m2).append(m3).append(m4)
    df1 = pd.read_csv('data/port1.csv')
    df2 = pd.read_csv('data/port2.csv')
    df3 = pd.read_csv('data/port3.csv')
    exemplo = pd.read_csv('data/Exemplo.csv')
########## Leitura dos dados ##########

########## Exemplo ##########
    if tela == "Exemplo com 3 Portfólios":
        # Filtrando df
        base = ['id','sg_uf','de_ramo','setor','nm_divisao','nm_segmento','de_nivel_atividade',
                'nm_meso_regiao','nm_micro_regiao','de_faixa_faturamento_estimado','idade_empresa_anos',
                'de_natureza_juridica','fl_me','fl_sa','fl_epp','fl_mei','fl_ltda','qt_filiais']
        df_nao_nulos = df[base]
        # Retirando as observações com nulos
        df_nao_nulos.fillna('SEM INFORMAÇÃO', inplace=True)

        # Transformando as colunas com o LabelEncoder
        colunas_transform = list(df_nao_nulos.select_dtypes(include=['object','bool']).columns)
        colunas_transform.remove('id')
        encoder = LabelEncoder()
        for label in colunas_transform:
            label_coluna = 'cod_' + label
            df_nao_nulos[label_coluna] = encoder.fit_transform(df_nao_nulos[label])

        # Adicionando identificação dos portifólios
        df1['portfolio'] = 1
        df2['portfolio'] = 2
        df3['portfolio'] = 3
        # Juntando os clientes
        df_clientes = df1.append(df2).append(df3)
        # Identificando os clientes na base de mercado e na base de não nulos
        df = df.join(df_clientes.set_index('id'), on='id')
        df_nao_nulos = df_nao_nulos.join(df_clientes.set_index('id'), on='id')
        # Preenchendo os demais portifolios do mercado como 0
        df['portfolio'].fillna(0, inplace=True)
        df_nao_nulos['portfolio'].fillna(0, inplace=True)

        # Selecionando dados de treino
        train = ['cod_de_natureza_juridica','cod_sg_uf','cod_de_ramo','cod_setor','cod_nm_divisao',
                 'cod_nm_segmento','cod_de_nivel_atividade','cod_nm_meso_regiao',
                 'cod_de_faixa_faturamento_estimado']
        X = df_nao_nulos[train]
        # Treinando modelo
        kmeans = KMeans(n_clusters = 4)
        kmeans.fit(X)
        # Adicionando as classe no df
        labels = kmeans.labels_
        df_nao_nulos['kmeans'] = labels

        # Classe mais intensa em cada portfolio
        class_port1 = df_nao_nulos.query('portfolio == 1')['kmeans'].value_counts().index[0]
        class_port2 = df_nao_nulos.query('portfolio == 2')['kmeans'].value_counts().index[0]
        class_port3 = df_nao_nulos.query('portfolio == 3')['kmeans'].value_counts().index[0]
        # Fazendo seleção do exemplo a ser explorado
        st.markdown('**Seleção do Portfólio Exemplo**')
        select_analise = st.radio('Escolha um portfólio abaixo :', ('Portfólio 1', 'Portfólio 2', 'Portfólio 3'), index=1)
        if select_analise == 'Portfólio 1':
            df_port = df_nao_nulos.query('kmeans == @class_port1 and portfolio not in ("1")').iloc[:,0:18]
        if select_analise == 'Portfólio 2':
            df_port = df_nao_nulos.query('kmeans == @class_port2 and portfolio not in ("2")').iloc[:,0:18]
        if select_analise == 'Portfólio 3':
            df_port = df_nao_nulos.query('kmeans == @class_port3 and portfolio not in ("3")').iloc[:,0:18]
        # Inicio exploração Portfólio Exemplo
        st.markdown('**Resumo dos Leads e variáveis disponívies**')
        st.dataframe(df_port.head())
        st.markdown('**Analise Gráfica dos Leds**')
        if st.checkbox("Leads por UF"):
            sns.catplot(x="sg_uf", 
                        kind="count", 
                        palette="ch:.25", 
                        data=df_port)
            plt.title('Quantidade de Leads por UF')
            plt.xlabel('UF')
            plt.ylabel('Qdt Leads')
            #plt.figure(figsize=(24,16))
            #plt.legend()
            st.pyplot()
        if st.checkbox("Leads por Setor"):
            treemap = df_port['setor'].value_counts()
            sizes = treemap.values
            label = treemap.index
            sqy.plot(sizes=sizes, label=label, alpha=.8 )
            plt.axis('off')
            #plt.figure(figsize=(24,16))
            st.pyplot()
        if st.checkbox("Top por Característica"):
            colunas = list(list(df_port.iloc[:,1:12].columns))
            opcao = st.selectbox('Selecione a opção de filtro', colunas)
            st.dataframe(df_port[opcao].value_counts())
        st.markdown('**Seleção de Leads por Filtro**')
        if st.checkbox("Seleção de Leads"):
            colunas = list(df_port.columns)
            opcao = st.selectbox('As colunas utilizadas para filtro', colunas)
            filtros = list(df_port[opcao].unique())
            selecao = st.selectbox('O valor utilizado para filtro', filtros)
            df_filter = df_port.loc[df_port[opcao] == selecao]
            head = st.slider('Quantos Leads?', 0, 100, 10)
            st.dataframe(df_filter.head(head))
        # Download dos Leads
        st.markdown('**Download Leads**')
        len_df_fat = int(df_port.shape[0]/2)
        df_dowload1 = df_port.reset_index().loc[:len_df_fat, :]
        df_dowload2 = df_port.reset_index().loc[len_df_fat+1:, :]
        st.markdown(get_table_download_link(df_dowload1, 'Download Parte 1'), unsafe_allow_html=True)
        st.markdown(get_table_download_link(df_dowload2, 'Download Parte 2'), unsafe_allow_html=True)

########## Exemplo ##########

########## Geração ##########
    if tela == "Gere Leads com seu Portfólio":
        st.markdown('**Gere Leads com seu Portfólio**')
        if st.checkbox("Exemplo arquivo CSV"):
            st.image('img/exemplo.png',format='PNG')
            st.markdown(get_table_download_link(exemplo, 'Download Arquivo Exemplo'), unsafe_allow_html=True)
        st.markdown('**Upload do seu Portfólio**')
        file  = st.file_uploader('Selecione o seu portfolio (.csv)', type = 'csv')
        if file is not None:
            exemplo = pd.read_csv(file)
            # Filtrando df
            base = ['id','sg_uf','de_ramo','setor','nm_divisao','nm_segmento','de_nivel_atividade',
                    'nm_meso_regiao','nm_micro_regiao','de_faixa_faturamento_estimado','idade_empresa_anos',
                    'de_natureza_juridica','fl_me','fl_sa','fl_epp','fl_mei','fl_ltda','qt_filiais']
            df_exemplo = df[base]
            df_exemplo = df_exemplo.append(exemplo)
            # Retirando as observações com nulos
            df_exemplo.fillna('SEM INFORMAÇÃO', inplace=True)
            
            # Transformando as colunas com o LabelEncoder
            colunas_transform = list(df_exemplo.select_dtypes(include=['object','bool']).columns)
            colunas_transform.remove('id')
            encoder_ex = LabelEncoder()
            for label in colunas_transform:
                label_coluna = 'cod_' + label
                df_exemplo[label_coluna] = encoder_ex.fit_transform(df_exemplo[label])
                #st.dataframe(df_exemplo.head())

            # Adicionando identificação do exemplo
            exemplo['portfolio'] = 1
            exemplo = exemplo[['id','portfolio']]

            # Identificando os clientes na base de mercado e na base de não nulos
            df_exemplo = df_exemplo.join(exemplo.set_index('id'), on='id')

            # Preenchendo os demais portifolios do mercado como 0
            df_exemplo['portfolio'].fillna(0, inplace=True)

            # Selecionando dados de treino
            train = ['cod_de_natureza_juridica','cod_sg_uf','cod_de_ramo','cod_setor','cod_nm_divisao','cod_nm_segmento',
                     'cod_de_nivel_atividade','cod_nm_meso_regiao','cod_de_faixa_faturamento_estimado']
            X_exemplo = df_exemplo[train]
            # Treinando modelo
            kmeans = KMeans(n_clusters = 4)
            kmeans.fit(X_exemplo)
            # Adicionando as classe no df
            labels = kmeans.labels_
            df_exemplo['kmeans'] = labels

            # Classe mais intensa em cada portfolio
            class_port_ex = df_exemplo.query('portfolio == 1')['kmeans'].value_counts().index[0]
            df_port_ex = df_exemplo.query('kmeans == @class_port_ex and portfolio not in ("1")').iloc[:,0:18]

            # Inicio exploração Portfólio Exemplo
            st.markdown('**Resumo dos Leads e variáveis disponívies**')
            st.dataframe(df_port_ex.head())
            st.markdown('**Analise Gráfica dos Leds**')
            if st.checkbox("Leads por UF"):
                sns.catplot(x="sg_uf", 
                            kind="count", 
                            palette="ch:.25", 
                            data=df_port_ex)
                plt.title('Quantidade de Leads por UF')
                plt.xlabel('UF')
                plt.ylabel('Qdt Leads')
                #plt.figure(figsize=(24,16))
                #plt.legend()
                st.pyplot()
            if st.checkbox("Leads por Setor"):
                treemap = df_port_ex['setor'].value_counts()
                sizes = treemap.values
                label = treemap.index
                sqy.plot(sizes=sizes, label=label, alpha=.8 )
                plt.axis('off')
                #plt.figure(figsize=(24,16))
                st.pyplot()
            if st.checkbox("Top por Característica"):
                colunas = list(list(df_port_ex.iloc[:,1:12].columns))
                opcao = st.selectbox('Selecione a opção de filtro', colunas)
                st.dataframe(df_port_ex[opcao].value_counts())
            st.markdown('**Seleção de Leads por Filtro**')
            if st.checkbox("Seleção de Leads"):
                colunas = list(df_port_ex.columns)
                opcao = st.selectbox('As colunas utilizadas para filtro', colunas)
                filtros = list(df_port_ex[opcao].unique())
                selecao = st.selectbox('O valor utilizado para filtro', filtros)
                df_filter_ex = df_port_ex.loc[df_port_ex[opcao] == selecao]
                head = st.slider('Quantos Leads?', 0, 100, 10)
                st.dataframe(df_filter_ex.head(head))
            # Download dos Leads
            st.markdown('**Download Leads**')
            len_df_fat = int(df_port_ex.shape[0]/2)
            df_dowload1 = df_port_ex.reset_index().loc[:len_df_fat, :]
            df_dowload2 = df_port_ex.reset_index().loc[len_df_fat+1:, :]
            st.markdown(get_table_download_link(df_dowload1, 'Download Parte 1'), unsafe_allow_html=True)
            st.markdown(get_table_download_link(df_dowload2, 'Download Parte 2'), unsafe_allow_html=True)


########## Geração ##########

########## main ##########


if __name__ == '__main__':
    main()
