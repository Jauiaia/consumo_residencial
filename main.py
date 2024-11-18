import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração inicial
st.set_page_config(page_title="Analisador de Consumo de Energia", layout="wide")

st.title("Analisador de Consumo de Energia Residencial")
st.markdown("""
Este webapp permite que você analise seu consumo de energia residencial ao longo de um mês.
Carregue um arquivo CSV com os dados de consumo para começar!
""")

# Upload do arquivo CSV
uploaded_file = st.file_uploader("Carregue seu arquivo CSV", type=["csv"])

if uploaded_file:
    # Leitura dos dados
    df = pd.read_csv(uploaded_file)
    
    # Validação de colunas essenciais
    required_columns = ['Data/Hora', 'Consumo em kWh', 'Custo Total']
    if not all(col in df.columns for col in required_columns):
        st.error(f"O arquivo deve conter as colunas: {', '.join(required_columns)}")
    else:
        # Processamento de dados
        df['Data/Hora'] = pd.to_datetime(df['Data/Hora'], errors='coerce')
        df = df.dropna(subset=['Data/Hora'])  # Remove linhas inválidas
        df['Data'] = df['Data/Hora'].dt.date
        df['Hora'] = df['Data/Hora'].dt.hour

        # Exibição dos dados
        st.subheader("Dados Carregados")
        st.dataframe(df)

        # Filtro de período
        st.sidebar.header("Filtros de Período")
        start_date = st.sidebar.date_input("Data de Início", value=min(df['Data']))
        end_date = st.sidebar.date_input("Data de Fim", value=max(df['Data']))

        if start_date > end_date:
            st.error("A data de início não pode ser maior que a data de fim.")
        else:
            # Filtragem dos dados
            filtered_df = df[(df['Data'] >= start_date) & (df['Data'] <= end_date)]
            
            # Consumo total por dia
            daily_consumption = filtered_df.groupby('Data').sum(numeric_only=True).reset_index()
            max_consumption_day = daily_consumption.loc[daily_consumption['Consumo em kWh'].idxmax()]
            
            st.subheader("Gráfico: Consumo Total por Dia")
            bar_fig = px.bar(
                daily_consumption,
                x='Data',
                y='Consumo em kWh',
                title='Consumo Total por Dia',
                labels={'Consumo em kWh': 'Consumo (kWh)'},
                color='Consumo em kWh',
                color_continuous_scale='Viridis',
            )
            bar_fig.add_annotation(
                x=max_consumption_day['Data'],
                y=max_consumption_day['Consumo em kWh'],
                text="Maior Consumo",
                showarrow=True,
                arrowhead=3
            )
            st.plotly_chart(bar_fig, use_container_width=True)

            # Consumo médio por hora
            hourly_consumption = filtered_df.groupby('Hora').mean(numeric_only=True).reset_index()
            st.subheader("Gráfico: Consumo Médio por Hora")
            line_fig = px.line(
                hourly_consumption,
                x='Hora',
                y='Consumo em kWh',
                title='Consumo Médio por Hora',
                labels={'Consumo em kWh': 'Consumo Médio (kWh)', 'Hora': 'Hora do Dia'},
            )
            st.plotly_chart(line_fig, use_container_width=True)

            # Distribuição percentual por categorias
            st.subheader("Gráfico: Distribuição Percentual")
            bins = [-1, 5, 17, 22, 24]
            labels = ['Madrugada', 'Pico', 'Noturno', 'Madrugada']
            filtered_df['Categoria'] = pd.cut(
                filtered_df['Hora'], bins=bins, labels=labels, right=False
            )
            category_consumption = filtered_df.groupby('Categoria').sum(numeric_only=True).reset_index()
            pie_fig = px.pie(
                category_consumption,
                values='Consumo em kWh',
                names='Categoria',
                title='Distribuição Percentual do Consumo'
            )
            st.plotly_chart(pie_fig, use_container_width=True)

            # Comparação entre consumo médio e consumo diário no período filtrado
            st.subheader("Comparação de Consumo")
            overall_daily_avg = df.groupby('Data')['Consumo em kWh'].sum().mean()
            period_daily_avg = filtered_df.groupby('Data')['Consumo em kWh'].sum().mean()
            st.write(f"**Consumo Médio Diário Geral:** {overall_daily_avg:.2f} kWh")
            st.write(f"**Consumo Médio Diário no Período Filtrado:** {period_daily_avg:.2f} kWh")

            # Consumo total e custo total no período filtrado
            st.sidebar.header("Resumo do Período")
            st.sidebar.write(f"*Consumo Total (kWh):* {filtered_df['Consumo em kWh'].sum():.2f}")
            st.sidebar.write(f"*Custo Total (R$):* {filtered_df['Custo Total'].sum():.2f}")

else:
    st.info("Por favor, carregue um arquivo CSV para começar.")

# Rodapé
st.markdown("""
---
*Desenvolvido por Iaia Jau | Analisador de Consumo de Energia Residencial*
""")