import os, sys, getopt, string
from pyparsing import *

SelectStmt = Forward()
expr = Forward()

LiteralValue = Word(alphanums)
BindParameter = Regex(".+?")
DatabaseName = Word(alphanums)
Dot = Literal(".")
TableName = Word(alphanums)
TableAlias = Word(alphanums)
IndexName = Word(alphanums)
ColumnName = Word(alphanums)
UnraryOperator = Word(alphanums)
BinaryOperator = Word(alphanums)
ColumnAlias = Word(alphanums)
CollationName = Word(alphanums)
TypeName = Word(alphanums)
AllColumns = Literal("*")
Comma = Literal(",")
LPAREN = Literal("(")
RPAREN = Literal(")")
FunctionName = Word(alphanums)
ISNULL,NOTNULL,NOT,NULL,IS,IN,EXISTS,CAST = map(CaselessKeyword,
            "isnull notnull not null is in exists cast".split())
COLLATE,ASC,DESC = map(CaselessKeyword,"collate asc desc".split())
SELECT,DISTINCT,ALL,FROM,WHERE,GROUP,HAVING = map(CaselessKeyword,
                "select distinct all from where group having".split())
AS = CaselessKeyword("as")

LIKE,GLOB,REGEXP,MATCH = map(CaselessKeyword,"like glob regexp match".split())
ESCAPE = CaselessKeyword("escape")

DbTable = Optional(DatabaseName+Dot)+TableName

expr << (LiteralValue | BindParameter | \
       Optional(DbTable + Dot) + ColumnName |\
       UnraryOperator + expr |\
       expr + BinaryOperator + expr |\
       FunctionName + LPAREN + Optional(AllColumns|Optional(DISTINCT)+delimitedList(expr)) + RPAREN |\
       LPAREN + expr + RPAREN |
       CAST + LPAREN + expr + AS + TypeName + RPAREN |\
       expr + COLLATE + CollationName |\
       expr + Optional(NOT) + Optional(LIKE|GLOB|REGEXP|MATCH) + expr + Optional(ESCAPE+expr) |\
       expr + Optional(ISNULL|NOTNULL|NOT+NULL) |\
       expr + IS + Optional(NOT) + expr |\
       expr + Optional(NOT) + IN + (LPAREN + Optional(SelectStmt|delimitedList(expr)) + RPAREN)^DbTable |\
       Optional(Optional(NOT) + EXISTS) + LPAREN + SelectStmt + RPAREN)



UNION,INTERSECT,EXCEPT = map(CaselessKeyword,
                                 "union intersect except".split())
ORDER,BY,LIMIT,OFFSET = map(CaselessKeyword, "order by limit offset".split())
NATURAL,LEFT,OUTER,INNER,CROSS,JOIN = map(CaselessKeyword,
                            "natural left outer inner cross join".split())

ON,USING = map(CaselessKeyword, "on using".split())
INDEXED,NOT = map(CaselessKeyword, "indexed not".split())



ResultColumn = AllColumns | TableName + Dot + AllColumns | \
               expr + Optional(Optional(AS) + ColumnAlias)

OrderingTerm = expr + Optional(COLLATE + CollationName) + Optional(ASC|DESC)



JoinOp = Comma | Optional(NATURAL) + \
            Optional(CROSS|INNER|LEFT+Optional(OUTER)) + JOIN

JoinConstraint = Optional(ON + expr | USING + LPAREN + \
                          delimitedList(ColumnName) + RPAREN)

JoinSource = Forward()

SingleSource = DbTable +\
               Optional(Optional(AS)+TableAlias) + \
               Optional(INDEXED + BY + IndexName | NOT + INDEXED) | \
               LPAREN + SelectStmt + RPAREN + Optional(Optional(AS) + \
               TableAlias) | LPAREN + JoinSource + RPAREN

JoinSource << (SingleSource + ZeroOrMore(JoinOp+SingleSource+JoinConstraint))

SelectCore = SELECT + Optional(DISTINCT|ALL) + delimitedList(ResultColumn) +\
             Optional(FROM + JoinSource) + Optional(WHERE + expr) + \
             Optional(GROUP + BY + delimitedList(OrderingTerm) + \
                      Optional(HAVING + expr))

CompoundOperator = UNION + Optional(ALL) |\
                   INTERSECT |\
                   EXCEPT

SelectStmt << (delimitedList(SelectCore, delim=CompoundOperator) +\
             Optional(ORDER + BY + delimitedList(OrderingTerm))+\
             Optional(LIMIT + expr + Optional((OFFSET|Comma) + expr)))






 
#arithSign = Word("+-",exact=1)
# 
#realNum = Combine( Optional(arithSign) + ( Word( nums ) + "." + Optional( Word(nums) ) |
#            ( "." + Word(nums) ) ) + Optional( E + Optional(arithSign) + Word(nums) ) )
#intNum = Combine( Optional(arithSign) + Word( nums ) +
#            Optional( E + Optional("+") + Word(nums) ) )
#keywords = DEFAULT | NULL | TRUE | FALSE
# 
#comment = "--" + restOfLine
# 
#name = ~major_keywords + Word(alphanums + alphas8bit + "_")
#value = realNum | intNum | quotedString | name | keywords # need to add support for alg expressions
# 
# 
##INSERT Statement
#"""
#    INSERT INTO table [ ( column [, ...] ) ]
#    { DEFAULT VALUES | VALUES ( { expression | DEFAULT } [, ...] ) [, ...] | query }
#    [ RETURNING * | output_expression [ AS output_name ] [, ...] ]
#    """
# 
#ins_columns = Group(delimitedList( name ))
#ins_values = Group(delimitedList( value ))
## define the grammar
#insert_stmt = INSERT + INTO + name.setResultsName( "table" ) \
#            + Optional( "(" + ins_columns.setResultsName( "columns" ) + ")") \
#            + VALUES + "(" + ins_values.setResultsName( "vals" ) + ")" + ';'
#insert_stmt.ignore( comment )
 
def select(query):
    try:
        ParserElement.enablePackrat()
        tokens = SelectStmt.parseString( query )
    except ParseException:
        return False
    else:
        return tokens
 
tokens = select("SELECT * FROM (select * from this);")
print tokens.dump()
