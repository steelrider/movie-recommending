import sys
import re
import csv
import copy
from random import randint
import math
from collections import Counter

#функция, която помага да се създаде потребител
def createUser(movies):
    id = input("Input ID: ");
    user = User(id,[],[]);
    print("Type ""exit"" to stop");
    while(True):
        title = input("Enter exact movie name: ");
        if(title=="exit"):
            break;
        score = input("Enter a rating for the movie: ");
        added = False;
        for movie in movies:
            if(int(title)==movie.id):
                user.addRating((movie.id,float(score)));
                user.addMovie(movie.id);
                added = True;
                break;
            else:
                continue;
        if(added==True):
            print("Rating added successfully");
            added = False;
            continue;
        else:
            print("Movie not found in dataset");
    return user;
#чете custom потребител от файл
def readUser(userName):
    with open(userName+".txt",'r') as csvfile:
        readCSV = csv.reader(csvfile,delimiter = ',');
        next(readCSV);
        for row in readCSV:
            if(row[0]=='userId'):
                continue;
            currentId = int(row[0]);
            currentUser = User(currentId,[],[]);
            currentUser.addRating((int(row[1]),float(row[2]))); 
            currentUser.addMovie(int(row[1]));
            for row in readCSV:
                if(row[0]=='userId'):
                    continue;
                if(int(row[0])==currentId):
                    currentUser.addRating((int(row[1]),float(row[2])));
                    currentUser.addMovie(int(row[1]));
    return currentUser;
              
#жанровете ги прави от стринг -> масив
def genresStringToList(text):
    genres = [];
    genre = "";
    for char in text:
        if(char!="|"):
            genre+=char;
        if(char=="|"):
            genres.append(genre);
            genre = "";
            continue;
    genres.append(genre); #добавяме и последния жанр
    return genres;
#compatability между 2ма потребителя, тоест колко % си приличат вкусовете на двамата
def commonRatings(user1,user2):
    common = 0;
    for rating in user1.movieRatings:
        if(rating in user2.movieRatings):
            common+=1;
    return (common/min(len(user1.movieRatings),len(user2.movieRatings)))*100;
#подобност между 2 филма спрямо жанровете
def commonGenres(top4s,movie):
    common = 0;
    for genre in top4s:
        if(genre in movie.genres):
            common+=1;
        else:
            continue;
    return (common/4)*100;
#взима топ 4 жанра за даден потребител спрямо филмите, които е оценил с над 3.5/5.0
def top4(user,movies):
    allGenres = []; #списък с всички жанрове за този потребител с повторения
    for rating in user.movieRatings:
        for movie in movies:
            if(rating[0]==movie.id and rating[1]>=3.5):
                for genre in movie.genres:
                    allGenres.append(genre);
                break;
            else:
                continue;
    c = Counter(allGenres);
    allGenres = [];
    for genre in c.most_common(4):
        allGenres.append(genre[0]);
    return allGenres;
#клас за филм
class Movie():
    def __init__(self,id,title,genres):
        self.id = id;
        self.title = title;
        self.genres = genresStringToList(genres);
    def printMovie(self):
        print("Movie ID:",self.id,'\n'
              "Movie title:",self.title,'\n'
              "Genres:");
        for genre in self.genres:
            print("-",genre);
        print("---------------------------------");
#клас за потребител
class User(): #id започват от 1000 нагоре, понеже последното userid в ratings е 671
    def __init__(self,id,movies,movieRatings): #movieRatings is list of tuples with (movieId,rating), movies is a list of movie ids, not objects!!
        self.id = id;
        self.movies = movies;
        self.movieRatings = movieRatings;
    def printUser(self):
        print("User ID:",self.id,'\n'
              "Movie Ratings:");
        for rating in self.movieRatings:
            print(rating);
        print("-------------------------");
    def addRating(self,rating):
        self.movieRatings.append(rating);
    def addMovie(self,movie):
        self.movies.append(movie);
            
#списък с филми, като обекти на клас Movie
movies = [];
#списък с потребители
users = [];

#reading from csv files
with open("movies.csv",'r',encoding="utf8") as csvfile:
    readCSV = csv.reader(csvfile,delimiter = ',');
    for row in readCSV:
        if(row[0]=="movieId"): #изпускаме първия ред от файла
            continue;
        else:
            movie = Movie(int(row[0]),row[1],row[2]);
            movies.append(movie);
#making users
with open("ratings.csv",'r') as csvfile:
    readCSV = csv.reader(csvfile,delimiter = ',');
    next(readCSV);
    for row in readCSV:
        if(row[0]=='userId'):
            continue;
        currentId = int(row[0]);
        currentUser = User(currentId,[],[]);
        currentUser.addRating((int(row[1]),float(row[2]))); 
        currentUser.addMovie(int(row[1]));
        for row in readCSV:
            if(row[0]=='userId'):
                continue;
            if(int(row[0])==currentId):
                currentUser.addRating((int(row[1]),float(row[2])));
                currentUser.addMovie(int(row[1]));
            if(int(row[0])==currentId+1):
                break;
        users.append(currentUser);
    

def recommend(customUser,users,movies):
    neibors = [];
    for user in users: #потребители със същия вкус спрямо оценките
        if(commonRatings(customUser,user)>=50.00):
            neibors.append(user);
        else:
            continue;
    neiborMovies = [];
    for neibor in neibors:
        for movieId in neibor.movies:
            for movie in movies:
                if(movieId==movie.id):
                    neiborMovies.append(movie);
                    break;
                else:
                    continue;
    myMovies = [];
    for movieId in customUser.movies:
        for movie in movies:
            if(movieId==movie.id):
                myMovies.append(movie);
                break;
            else:
                continue;
    toRecommend = [];
    usersTop4 = top4(customUser,movies);
    for movie in neiborMovies:
        if(commonGenres(usersTop4,movie)>=75.00 and movie not in toRecommend and movie.id not in customUser.movies):
            toRecommend.append(movie);
    for movie in toRecommend:
        movie.printMovie();
    print("You matched with the following users (id): ");
    for neibor in neibors:
        print(neibor.id);
    print("Your top 4 favourite genres are: ");
    print(usersTop4);
            
#примерни потребители
customUser1 = readUser("testUser1");
customUser2 = readUser("testUser2");
recommend(customUser1,users,movies);
