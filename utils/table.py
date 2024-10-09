import streamlit as st
import pandas as pd

class Column:
    def __init__(self, name, header, footer_fn=None):
        """
        :param name: Name of the column in the dataframe.
        :param header: Header string to display at the top of the column.
        :param footer_fn: Optional function to calculate the footer (e.g., sum of the column).
        """
        self.name = name
        self.header = header
        self.footer_fn = footer_fn

    def render_header(self, cols, idx):
        """Render the header for this column."""
        with cols[idx]:
            st.write(f"**{self.header}**")
    
    def render_cell(self, cols, idx, row, df, row_idx, input_fn=None):
        """Render a cell in the column and update the DataFrame."""
        with cols[idx]:
            value = row[self.name]
            if input_fn:
                # If an input function is provided, update the dataframe with the new value
                df.loc[row_idx, self.name] = input_fn(value)
            else:
                # Otherwise, just display the value
                st.write(value)

    def render_footer(self, cols, idx, df):
        """Render the footer for this column."""
        if self.footer_fn:
            with cols[idx]:
                footer_value = self.footer_fn(df[self.name])
                st.write(f"**{footer_value}**")


class Table:
    def __init__(self, columns):
        """
        :param columns: A list of Column objects representing the table structure.
        """
        self.columns = columns
    
    def render_headers(self):
        """Render the headers of the table."""
        cols = st.columns(len(self.columns))
        for idx, col in enumerate(self.columns):
            col.render_header(cols, idx)
    
    def render_rows(self, df, input_fns=None):
        """Render the rows of the table and apply any input functions for each cell."""
        if input_fns is None:
            input_fns = [None] * len(self.columns)  # No input functions if not provided
        for row_idx, row in df.iterrows():
            cols = st.columns(len(self.columns))
            for idx, col in enumerate(self.columns):
                col.render_cell(cols, idx, row, df, row_idx, input_fns[idx])
    
    def render_footers(self, df):
        """Render the footers of the table."""
        cols = st.columns(len(self.columns))
        for idx, col in enumerate(self.columns):
            col.render_footer(cols, idx, df)


# --- Example Usage in the Streamlit App ---

# Example data
df = pd.DataFrame({
    "Nom": ["Room A", "Room B"],
    "Superficie chambre": [15, 18],
    "Apport": [50000, 60000],
    "Part": [0, 0],
    "Emprunt": [0, 0],
    "Mensualite": [0, 0]
})

# Constants
prix = 300000
cout_global = 500000
mensualite_totale = 2000
poids_chambres = 0.6

# Create table columns
table_columns = [
    Column("Nom", "Nom"),
    Column("Superficie chambre", "Superficie chambre (m²)", footer_fn=lambda col: col.sum()),
    Column("Part", "Part détenue"),
    Column("Apport", "Apport", footer_fn=lambda col: col.sum()),
    Column("Emprunt", "Emprunt", footer_fn=lambda col: col.sum()),
    Column("Mensualite", "Mensualité", footer_fn=lambda col: col.sum()),
]

# Create table object
table = Table(table_columns)

# Render headers
table.render_headers()

# Define input functions for columns that allow user input
input_functions = [
    None,  # "Nom" doesn't need input
    lambda val: st.slider("Superficie", min_value=6, max_value=20, value=val, step=1, label_visibility="collapsed"),
    None,  # "Part" is calculated and not input
    lambda val: st.slider("Apport", min_value=0, max_value=100000, value=val, step=1000, label_visibility="collapsed"),
    None,  # "Emprunt" is calculated and not input
    None,  # "Mensualite" is calculated and not input
]

# Render rows (with sliders where applicable)
table.render_rows(df, input_fns=input_functions)

# Render footers (e.g., totals)
table.render_footers(df)
