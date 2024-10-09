import streamlit as st
import pandas as pd

class TableColumn:
    def __init__(self, name, input_fn=None, footer_fn=None):
        """
        :param name: Name of the column in the dataframe (used for header and data input/output).
        :param input_fn: Optional function to handle input for the column (e.g., sliders).
        :param footer_fn: Optional function to calculate the footer (e.g., sum of the column).
        """
        self.name = name
        self.input_fn = input_fn
        self.footer_fn = footer_fn

    def render_header(self, cols, idx):
        """Render the header for this column (using the column name)."""
        with cols[idx]:
            st.write(f"**{self.name}**")
    
    def render_cell(self, cols, idx, row, df, row_idx):
        """Render a cell in the column and update the DataFrame if an input function is provided."""
        with cols[idx]:
            value = row[self.name]
            if self.input_fn:
                # If an input function is provided, update the dataframe with the new value
                df.loc[row_idx, self.name] = self.input_fn(value)
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
        :param columns: A list of TableColumn objects representing the table structure.
        """
        self.columns = columns

    def render(self, df):
        """Render the entire table including headers, rows, and footers."""
        # Render headers
        self.render_headers()
        
        # Render rows
        self.render_rows(df)
        
        # Render footers
        self.render_footers(df)

    def render_headers(self):
        """Render the headers of the table."""
        cols = st.columns(len(self.columns))
        for idx, col in enumerate(self.columns):
            col.render_header(cols, idx)
    
    def render_rows(self, df):
        """Render the rows of the table and apply any input functions for each cell."""
        for row_idx, row in df.iterrows():
            cols = st.columns(len(self.columns))
            for idx, col in enumerate(self.columns):
                col.render_cell(cols, idx, row, df, row_idx)
    
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
    TableColumn("Nom"),  # No input or footer function needed for this column
    TableColumn(
        "Superficie chambre",
        input_fn=lambda val: st.slider("Superficie", min_value=6, max_value=20, value=val, step=1, label_visibility="collapsed"),
        footer_fn=lambda col: col.sum()
    ),
    TableColumn("Part", footer_fn=None),  # "Part" calculated elsewhere, no input needed
    TableColumn(
        "Apport",
        input_fn=lambda val: st.slider("Apport", min_value=0, max_value=100000, value=val, step=1000, label_visibility="collapsed"),
        footer_fn=lambda col: col.sum()
    ),
    TableColumn("Emprunt", footer_fn=lambda col: col.sum()),
    TableColumn("Mensualite", footer_fn=lambda col: col.sum()),
]

# Create table object
table = Table(table_columns)

# Render the entire table with a single call
table.render(df)
