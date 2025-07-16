def build_query(base_query, date_from=None, date_to=None, limit=None):
    clauses = []
    if date_from:
        clauses.append(f"date >= '{date_from}'")
    if date_to:
        clauses.append(f"date <= '{date_to}'")
    where_clause = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    limit_clause = f" TOP {limit}" if limit else ""
    return base_query.format(where=where_clause, limit=limit_clause)
