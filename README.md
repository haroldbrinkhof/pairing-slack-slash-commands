# pairing-slack-slash-commands
slash commands for a slack team that enable users to:
 - set themselves as available for code pairing (per channel)
 - for others to check who is available for pairing (per channel)
 - retrieve and keep statistics on pairing habits
 
 **/pairing** returns the list of people in the channel available for pairing 
          (per channel so you can use it as a differentiator/filter)
          
**/pairing** *yes*|*on*: mark yourself as available for pairing (for this channel)

**/pairing** *no*|*off*: mark yourself as unavailable for pairing (for this channel)

**/pairing-with** *@username*: mark yourself as pairing with a person

**/pairing-end**: mark your current pairing as finished

**/pairing-statistics**: should return statistics on a weekly basis, not yet implemented, 
                          functionality TBD.
