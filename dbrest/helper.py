from flask_sqlalchemy import BaseQuery

def get_malette_id():
    return 1  # TODO read this value from a file or from a server...

class CompositePrimaryKeyHackedQuery(BaseQuery):
    def filter(self, *criterion):
        """
        A big hack that allow using an unique primary_key to find a table with composite key
        You'll have to separate every key by '-'

        E.g: with a table like
            class Test(db.Model):
                id1 = db.Column(db.Integer, primary_key=True)
                id2 = db.Column(db.Integer, primary_key=True)
            you can do:
                >>> session.query().filter(Test.id1 == '1-2')

            It will be the same as
                >>> session.query().filter(Test.id1 == 1, Test.id2 == 2)

        Because this hack is used for flask_restless if you only give a part of the query
        E.g
            >>> session.query().filter(Test.id1 == 1)

        It will return an impossible query (to get a 404)
        """

        SEP = "-"

        ncriterion = []
        for crit in criterion:
            ncrits = []

            col = crit.left
            val = crit.right.effective_value

            primary_key_cols = col.table.primary_key
            if col.primary_key and SEP in val:
                vals = val.split(SEP)

                if len(vals) != len(primary_key_cols):
                    return super().filter(col == 1, col == 0)  # Should be a 404, so generate an impossible query

                for v, primary_key_col in zip(vals, primary_key_cols):
                    ncrits.append(primary_key_col == v)

                if ncrits:
                    ncriterion += ncrits
            else:
                ncriterion.append(crit)

        return super().filter(*ncriterion)
