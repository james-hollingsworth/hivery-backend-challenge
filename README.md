# Paranuara Challenge Solution
## Prerequisites
You are running the solution on Linux with Python 3 installed, and a Python 3 virtualenv created and activated:
E.g.
```
virtualenv -p python3 solution
. ./solution/bin/activate
```

## To install
This code depends on version 2.x of Django.  To install requirements and also import
the datafiles associated with the challenge run:
```
make install
```
Note that as SQLITE was used to minimise configuration requirements the data import takes several minutes

## To run all unit tests
Before running the project for the first time, you can run the entire suite of unit
tests to verify the solution is installed correctly:
```
make test
```

## To run the solution
The solution uses Django to provide a REST api.  To fire up Django's build in server:
```
make run
```
You can then use the URLs described below from a web-browser, cURL etc to interact with the solution

### To view all employees of a supplied company
Enter a url in the following format:
```
http://127.0.0.1:8000/api/company_employees/<company_id>
```
Where _<company_id>_ can be either the numeric ID (index) or case-sensitive name (spaces represented as %20) of the company

E.g. http://127.0.0.1:8000/api/company_employees/PERMADYNE

### To view the friends with brown eyes that are alive that are friends of two people
Enter a url in the following format:
```
http://127.0.0.1:8000/api/common_friends/<person1_id>/<person2_id>?eye_colour=[BR|BL|GR|GY|AL|OT]&is_alive=[True|False]
```
Where:
 * _<person1_id>_ and _<person2_id>_ can be either the numeric ID (index) or case-sensitive name (spaces represented as %20) of the person
 * The eye_colour codes are:
 
 | Code  | Colour |
 | ----- | ------ |
 | BR    | Brown  |
 | BL    | Blue   |
 | GR    | Green  |
 | GY    | Grey   |
 | AL    | Albino |
 | OT    | Other  |
 
 E.g. http://127.0.0.1:8000/api/common_friends/1/2?eye_colour=BR&is_alive=True
 
 Note that you can query the friends in common of any number of people.  So for example to query the friends in common of 
 people with ID's 3, 77 & 100 you would do this:
 
 http://127.0.0.1:8000/api/common_friends/3/77/100?eye_colour=BR&is_alive=True
 
 In addition you can query any field available on a Person object.  So if you wanted to find all friends in 
 common between Henderson Petty and Claire Kline who were female:
 
 http://127.0.0.1:8000/api/common_friends/Henderson%20Petty/Claire%20Kline?gender=F
 
### To view the favourite fruit and vegetables of a person
Enter a url in the following format:
```
http://127.0.0.1:8000/api/favourite_food/<person_id>
```
  
Where _<person_id>_ can be either the numeric ID (index) or case-sensitive name (spaces represented as %20) of the person  

E.g. http://127.0.0.1:8000/api/favourite_food/2