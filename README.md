# COMS-W4111-Project-1

## Weijie Cai (wc2756) Matthew Kersey (mlk2194)

### USAGE

To use, set up a virtual environment and activate it. You can install the requirements using `pip install -r requirements.txt`. You will also need to create a .env file. It only needs two lines:  

```plaintext

DBUSER=<Username>  
DBPASS=<Password>

```

### POSTGRES ACCOUNT

Our PostgreSQL username is mlk2194

### URL OF OUR APP

Please find our app at http://35.236.207.213:8111/

### PROPOSAL IMPLEMENTATION

We implemented almost all parts of our proposal with two main exceptions:  
**1. Profile Pictures**
We did not add a column for profile pictures to our __users__ table in part 2. This combined with the complexity of implementing this from a frontend perspective encouraged us to focus on other features.
**2. Reporting Comments**
Again, we did not add a table for this in part 2, and we felt that the yield would be pretty minor from a user's perspective.  
We were able to implement the rest of our proposal, including users being able to register, login, post comments, like comments, delete comments, and view games, players, and teams for our four sports. We additionally implemented the search bar functionality we mentioned, which is capable of returning game, player, and team pages in the same query.

### INTERESTING PAGES

**1. Search Page (POST /search/)**
Our search page performs three queries to get information about players, games, and teams that match the criteria. The queries return a comprehensive list of the three types. If you search "Boston", you will get all games that have been played by teams from Boston, all teams from Boston, and even all players that have been on a team from Boston. To do this, we used the LIKE operator on fields across multiple tables. Additionally, we included comment count in our SELECT statement so that we could sort the results of the search by comment count and return it to the user.

**2. Comment Deletion (POST /comments/delete/)**
This "page" has a relatively simple set of queries that supports it. What we find interesting about it is that it has to delete entries from five tables in a specific order. Since the primary key of the __comments_post__ table appears as a foreign key in four other tables, we have to delete possible entries in those first.
