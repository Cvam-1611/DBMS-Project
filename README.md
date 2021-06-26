
# SMART MOVIE REVIEW SYSTEM

## Description
Smart Movie Review System is a Web application through which a person can give reviews for different movies. The review is then subjected to a sentiment analysis, which determines if the review is Highly Negative, Negative, Neutral, Positive, or Highly Positive, and assigns a rating accordingly, all of this occurs in real time.

## Framework
This web application has been built using **FLASK** framework

## Components for Front End
1. HTML
2. CSS
3. Bootstrap

## Database
**Language : MySQL** \
Database contains three tables namely
1. Accounts(contains details of all users)
2. Movie(contains details of all movies)
3. Mov_review(contains reviews and corresponding rating)

## Machine Learning Model
A movie review dataset was used to train the machine learning model, which comprises reviews and their related ratings.
The training/testing was done on 5 classification algorithm namely
1. **Logistic Regression**
2. **SVC Classifier**
3. **Random Forest Classifier**
4. **K Nearest Neighbour**
5. **Naive Bayes**
6. **XgBoost**

**The SVC classifier has performed well with an accuracy of 63.27%**



