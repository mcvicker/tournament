import time
import psycopg2

pg = psycopg2.connect("dbname=forum")
c = pg.cursor()
c.execute ("select * from posts")
number_1 = c.fetchall()
c.execute("Insert into posts values ('python api test')")
c.execute ("select * from posts;")
number_2 = c.fetchall()
pg.commit()
print
print "Rows"
for row in number_1:
	print "  ", row[0]
for row in number_2:
	print "  ", row[0]
print "testing this"
pg.close()