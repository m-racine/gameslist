CREATE VIEW top_priority as
SELECT * FROM top_priority_helper as a

WHERE (SELECT COUNT(*)
      from top_priority_helper as b
      WHERE b.system = a.system AND b.priority >= a.priority) <= 1
ORDER BY priority DESC;



CREATE VIEW top_priority_helper as SELECT
    g.*

FROM gameslist_game g

LEFT OUTER JOIN gameslist_gametoinstance gi
    ON g.id=gi.game_id

LEFT OUTER JOIN gameslist_gameinstance i
    ON gi.instance_id=i.id

WHERE
  gi.primary = 1;













GROUP BY top_priority.id, top_priority.system;



SELECT a.person, a.group, a.age FROM person AS a
WHERE (SELECT COUNT(*)
        FROM person AS b
        WHERE b.group = a.group AND b.age >= a.age) <= 2
ORDER BY a.group ASC, a.age DESC


SELECT * FROM top_priority AS a
WHERE (SELECT COUNT(*)
      FROM top_priority AS b
      WHERE b.system = a.system AND b.priority > a.priority) <= 1
ORDER BY a.priority DESC
