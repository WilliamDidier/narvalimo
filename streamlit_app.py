import streamlit as st
import pandas as pd
import json
import plotly.graph_objects as go


st.set_page_config(layout="wide")


@st.cache_data
def get_initial_df() -> pd.DataFrame:
    with open("init.json") as f:
        data = json.load(f)
    return pd.DataFrame(data)


@st.cache_data
def calculer_amortissement(emprunt, mensualite, taux_mensuel, duree):
    df = pd.DataFrame(
        columns=["Mois", "Capital restant", "Intérêts", "Capital remboursé"]
    )
    capital_restant = emprunt

    for mois in range(1, duree + 1):
        interets = capital_restant * taux_mensuel
        capital_rembourse = mensualite - interets
        capital_restant -= capital_rembourse

        df.loc[len(df.index)] = {
            "Mois": mois,
            "Capital restant": capital_restant,
            "Intérêts": interets,
            "Capital remboursé": capital_rembourse,
        }
    return df


def creer_graphique_amortissement(df_amort, titre):
    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df_amort["Mois"],
            y=df_amort["Capital remboursé"].cumsum(),
            mode="lines",
            name="Capital remboursé",
            hovertemplate="Capital remboursé: %{y:.0f}€<extra></extra>",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=df_amort["Mois"],
            y=df_amort["Intérêts"].cumsum(),
            mode="lines",
            name="Intérêts cumulés",
            hovertemplate="Intérêts cumulés: %{y:.0f}€<extra></extra>",
        )
    )

    fig.update_layout(
        title=titre,
        xaxis_title="Mois",
        yaxis_title="Montant (€)",
        hovermode="x unified",
    )

    return fig


# Crée une appli Streamlit pour calculer l'amortissement d'un achat immobilier
def app():
    st.title("Bien")
    prix = int(st.number_input("Valeur du bien", min_value=0, value=545000))
    frais = int(st.number_input("Frais", min_value=0, value=int(0.11 * prix)))
    cout_global = prix + frais

    superficie_totale = st.number_input(
        "Superficie totale du bien en m²", min_value=20, value=180
    )

    st.metric("Coût total du projet", cout_global)

    st.title("Emprunt")
    taux = st.slider(
        "Taux d'emprunt", min_value=0.0, max_value=7.0, step=0.01, value=3.8
    )
    duree = st.slider(
        "Durée du prêt en mois", max_value=25 * 12, min_value=5 * 12, value=20 * 12
    )

    st.title("Apports & parts")
    df = get_initial_df()

    cols = st.columns(3)
    with cols[0]:
        st.write("**Nom**")
    with cols[1]:
        st.write("**Superficie chambre (m²)**")

    # Initialisation des variables avec des valeurs par défaut
    superficie_chambres = df["Superficie chambre"].sum()
    superficie_communs = superficie_totale - superficie_chambres

    for idx, row in df.iterrows():
        cols = st.columns(2)
        nom = row["Nom"]
        superficie_chambre = row["Superficie chambre"]
        with cols[0]:
            st.write(nom)

        with cols[1]:
            df.loc[idx, "Superficie chambre"] = st.slider(
                f"Superficie {nom}",
                min_value=6,
                max_value=20,
                value=superficie_chambre,
                step=1,
                label_visibility="collapsed",
            )

    apport_total = df["Apport"].sum()
    superficie_chambres = df["Superficie chambre"].sum()

    cols = st.columns(3)
    with cols[0]:
        st.write("**Total**")
    with cols[1]:
        st.write(f"{apport_total}")
    with cols[2]:
        st.write(f"{superficie_chambres}")

    emprunt_total = cout_global - apport_total
    taux_mensuel = taux / 100 / 12
    mensualite_totale = (
        emprunt_total
        * (taux_mensuel * (1 + taux_mensuel) ** duree)
        / ((1 + taux_mensuel) ** duree - 1)
    )

    superficie_chambres = df["Superficie chambre"].sum()
    poids_chambres = st.slider(
        "Poids des chambres dans la répartition des parts (laisser par défaut pour une répartition au m²)",
        min_value=0.0,
        max_value=1.0,
        value=superficie_chambres / superficie_totale,
        step=0.01,
    )

    df[["Part", "Emprunt", "Mensualite"]] = None
    cols = st.columns(6)
    with cols[0]:
        st.write("**Nom**")
    with cols[1]:
        st.write("**Part détenue**")
    with cols[2]:
        st.write("**Valeur**")
    with cols[3]:
        st.write("**Apport**")
    with cols[4]:
        st.write("**Emprunt**")
    with cols[5]:
        st.write("**Mensualité**")

    for idx, row in df.iterrows():
        cols = st.columns(6)
        with cols[0]:
            st.write(row["Nom"])
        with cols[1]:
            part_detenue = row[
                "Superficie chambre"
            ] / superficie_chambres * poids_chambres + 1 / len(df) * (
                1 - poids_chambres
            )
            df.loc[idx, "Part"] = part_detenue
            st.write(round(part_detenue, 2))
        with cols[2]:
            valeur_part = part_detenue * prix
            st.write(round(valeur_part, 2))
        with cols[3]:
            df.loc[idx, "Apport"] = st.slider(
                f"Apport bite {row['Nom']}",
                min_value=0,
                max_value=100000,
                value=row["Apport"],
                step=1000,
                label_visibility="collapsed",
            )
        with cols[4]:
            prix_chambre = part_detenue * cout_global
            emprunt_perso = prix_chambre - df.loc[idx, "Apport"]
            df.loc[idx, "Emprunt"] = emprunt_perso
            st.write(round(emprunt_perso, 2))
        with cols[5]:
            mensualite = emprunt_perso / emprunt_total * mensualite_totale
            df.loc[idx, "Mensualite"] = mensualite
            st.write(round(mensualite, 2))

    cols = st.columns(6)
    with cols[0]:
        st.write("**Total**")
    with cols[1]:
        st.write(round(df["Part"].sum(), 2))
    with cols[4]:
        st.write(round(df["Emprunt"].sum(), 2))
    with cols[5]:
        st.write(round(df["Mensualite"].sum(), 2))

    st.download_button(
        label="Télécharger les données",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="data.csv",
        mime="text/csv",
    )

    tab_global, *tabs_individuels = st.tabs(["Global"] + list(df["Nom"]))
    # Onglet global
    with tab_global:
        df_amort_global = calculer_amortissement(
            emprunt_total, mensualite_totale, taux_mensuel, duree
        )
        fig_global = creer_graphique_amortissement(
            df_amort_global, "Évolution de l'amortissement global dans le temps"
        )
        st.plotly_chart(fig_global)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Apport initial", f"{apport_total:,.0f}€")
        with col2:
            st.metric("Montant emprunté", f"{emprunt_total:,.0f}€")
        with col3:
            st.metric("Mensualité", f"{mensualite_totale:,.2f}€")
        st.download_button(
            label="📥 Télécharger le tableau d'amortissement global",
            data=df_amort_global.to_csv(index=False),
            file_name="amortissement.csv",
            mime="text/csv",
        )
        with st.expander("👀 Afficher le tableau d'amortissement"):
            st.dataframe(df_amort_global, hide_index=True)

    # Onglets individuels
    for tab, (idx, row) in zip(tabs_individuels, df.iterrows()):
        with tab:
            df_amort_indiv = calculer_amortissement(
                row["Emprunt"], row["Mensualite"], taux_mensuel, duree
            )
            fig_indiv = creer_graphique_amortissement(
                df_amort_indiv,
                f"Évolution de l'amortissement pour {row['Nom']} dans le temps",
            )
            st.plotly_chart(fig_indiv)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Apport initial", f"{row['Apport']:,.0f}€")
            with col2:
                st.metric("Montant emprunté", f"{row['Emprunt']:,.0f}€")
            with col3:
                st.metric("Mensualité", f"{row['Mensualite']:,.2f}€")
            st.download_button(
                label=f"📥 Télécharger le tableau d'amortissement de {row['Nom']}",
                data=df_amort_indiv.to_csv(index=False),
                file_name=f"amortissement_{row['Nom']}.csv",
                mime="text/csv",
            )
            with st.expander(f"👀 Afficher le tableau d'amortissement de {row['Nom']}"):
                st.dataframe(df_amort_indiv, hide_index=True)

    # Ajout des sliders pour les superficies des chambres et le nombre d'occupants
    st.subheader("Répartition des chambres et des communs")
    if superficie_communs < 0:
        st.error(
            f"Erreur : La somme des superficies des chambres dépasse la superficie totale du bien : {superficie_chambres} > {superficie_totale}"
        )
        return

    fig = go.Figure(
        data=[
            go.Pie(
                labels=["Superficie des chambres", "Superficie des parties communes"],
                values=[superficie_chambres, superficie_communs],
            )
        ]
    )

    # Set title and display
    fig.update_layout(title_text="Superficie des chambres et parties communes")
    st.plotly_chart(fig)


if "page" not in st.session_state:
    st.session_state.page = "app"


if st.session_state.page == "app":
    app()


elif st.button("Revenir à l'accueil"):
    st.session_state.page = "accueil"
