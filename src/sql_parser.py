import os, sys, getopt, string
from pyparsing import *

SelectStmt = Forward()
expr = Forward()

NumericLiteral = (Word(nums) + Optional(Dot + Word(nums)) |\
                 Dot + Word(nums)) +\
                 Optional(Literal("E") + Optional(OneOf("+ -")) + Word(nums))

StringLiteral = Word(alphanums+"_")

NULL,CURRENT_TIME,CURRENT_DATE,CURRENT_TIMESTAMP = map(CaselessKeyword,
                "null current_time current_date current_timestamp".split())
literalValue = NumericLiteral |\
               StringLiteral |\
               NULL |\
               CURRENT_TIME |\
               CURRENT_DATE |\
               CURRENT_TIMESTAMP


DatabaseName = Word(alphanums+"_")
Dot = Literal(".")
TableName = Word(alphanums+"_")
TableAlias = Word(alphanums+"_")
IndexName = Word(alphanums+"_")
ColumnName = Word(alphanums+"_")
UnraryOperator = OneOf("- + ~")
BinaryOperator = OneOf("+ - / * % & |") | Literal("||") |\
                 Literal(">>", "<<",
ColumnAlias = Word(alphanums+"_")
CollationName = Word(alphanums+"_")
TypeName = Word(alphanums+"_")
AllColumns = Literal("*")
Comma = Literal(",")
LPAREN = Literal("(")
RPAREN = Literal(")")
FunctionName = Word(alphanums+"_")
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



ResultColumn = AllColumns | \
               TableName + Dot + AllColumns | \
               expr + Optional(Optional(AS) + ColumnAlias)
               

OrderingTerm = expr + Optional(COLLATE + CollationName) + Optional(ASC|DESC)



JoinOp = Comma | Optional(NATURAL) + \
            Optional(CROSS|INNER|LEFT+Optional(OUTER)) + JOIN

JoinConstraint = Optional(ON + expr | USING + LPAREN + \
                          delimitedList(ColumnName) + RPAREN)

SingleSource = Forward()
JoinSource = SingleSource + ZeroOrMore(JoinOp+SingleSource+JoinConstraint)

SingleSource << (DbTable +\
               Optional(AS+TableAlias) + \
               Optional(INDEXED + BY + IndexName | NOT + INDEXED) | \
               LPAREN + SelectStmt + RPAREN + Optional(Optional(AS) + \
               TableAlias) | LPAREN + JoinSource + RPAREN)



SelectCore = SELECT + Optional(DISTINCT|ALL) + delimitedList(ResultColumn) +\
             Optional(FROM + JoinSource) + Optional(WHERE + expr) + \
             Optional(GROUP + BY + delimitedList(OrderingTerm) + \
                      Optional(HAVING + expr))

CompoundOperator = UNION + Optional(ALL) |\
                   INTERSECT |\
                   EXCEPT

SelectStmt << (SelectCore + ZeroOrMore(CompoundOperator+SelectCore) +\
             Optional(ORDER + BY + delimitedList(OrderingTerm))+\
             Optional(LIMIT + expr + Optional((OFFSET|Comma) + expr)))

 
def select(query):
    try:
        #ParserElement.enablePackrat()
        tokens = SelectStmt.parseString(query)
    except ParseException:
        return False
    else:
        return tokens
 
tokens = select("SELECT date FROM test")
print tokens.dump()
