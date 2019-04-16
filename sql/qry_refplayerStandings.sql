DO $$
DECLARE
    @tour_id INTEGER := 1;

BEGIN
/*  
    Returns a list of the players and their win records, sorted by wins.
    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    | Begin Python parsing |
*/
    ;WITH WinCount AS
    (
        SELECT
            winner_id, 
            count(winner_id) AS win 
        FROM 
            Match
        WHERE tournament_id = @tour_id
        GROUP BY winner_id
    ),
    MatchCount AS
    (
        SELECT DISTINCT
            regplyr.player_id,
            COALESCE(MAX(mthwin.round), MAX(mthlss.round)) AS round
        FROM 
            Register AS regplyr
        LEFT JOIN Match mthwin ON regplyr.player_id = mthwin.winner_id
        LEFT JOIN Match mthlss ON regplyr.player_id = mthlss.loser_id
        WHERE regplyr.tournament_id = @tour_id
        GROUP BY regplyr.player_id
    )
    SELECT 
        regplyr.player_id,
        plyr.name,
        COALESCE(wc.win, 0) AS win,
        COALESCE(rnd.round, 0) AS matches
    FROM
        Register AS regplyr
    INNER JOIN Player AS plyr ON regplyr.player_id = plyr.id
    LEFT JOIN WinCount AS wc ON regplyr.player_id = wc.winner_id
    LEFT JOIN MatchCount AS rnd ON regplyr.player_id = rnd.player_id
    ORDER BY wc.win DESC;
/* | End Python parsing | */
END $$