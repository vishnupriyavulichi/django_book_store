from email.mime.multipart import MIMEMultipart
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Category, Writer, Book, Review, Slider
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .forms import RegistrationForm, ReviewForm
from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pyotp
from .forms import EmailForm


# Gmail credentials
GMAIL_USERNAME = "aasrithamanyam@gmail.com"
GMAIL_PASSWORD = "ljkj sbro odoi mlci"
auth:any

# Secret key for OTP generation (replace this with your own secret)
SECRET_KEY = "BLVM3YKJXITINJCG"

app = Flask(__name__)


def index(request):
    newpublished = Book.objects.order_by('-created')[:15]
    slide = Slider.objects.order_by('-created')[:3]
    context = {
        "newbooks":newpublished,
        "slide": slide
    }
    return render(request, 'store/index.html', context)


def signin(request):
    if request.user.is_authenticated:
        return redirect('store:index')
    else:
        if request.method == "POST":
            user = request.POST.get('user')
            password = request.POST.get('pass')
            print(user)
            print(password)
            auth = authenticate(request, username=user, password=password)
            if auth is not None:
                login(request, auth)
                return redirect('store:index')
            else:
            	messages.error(request, 'username and password doesn\'t match')

    return render(request, "store/login.html")	


def signout(request):
    logout(request)
    return redirect('store:index')	


def registration(request):
	form = RegistrationForm(request.POST or None)
	if form.is_valid():
		form.save()
		return redirect('store:signin')

	return render(request, 'store/signup.html', {"form": form})

def payment(request):
    return render(request, 'store/payment.html')


def get_book(request, id):
    form = ReviewForm(request.POST or None)
    book = get_object_or_404(Book, id=id)
    rbooks = Book.objects.filter(category_id=book.category.id)
    r_review = Review.objects.filter(book_id=id).order_by('-created')

    paginator = Paginator(r_review, 4)
    page = request.GET.get('page')
    rreview = paginator.get_page(page)

    if request.method == 'POST':
        if request.user.is_authenticated:
            if form.is_valid():
                temp = form.save(commit=False)
                temp.customer = User.objects.get(id=request.user.id)
                temp.book = book          
                temp = Book.objects.get(id=id)
                temp.totalreview += 1
                temp.totalrating += int(request.POST.get('review_star'))
                form.save()  
                temp.save()

                messages.success(request, "Review Added Successfully")
                form = ReviewForm()
        else:
            messages.error(request, "You need login first.")
    context = {
        "book":book,
        "rbooks": rbooks,
        "form": form,
        "rreview": rreview
    }
    return render(request, "store/book.html", context)


def get_books(request):
    books_ = Book.objects.all().order_by('-created')
    paginator = Paginator(books_, 10)
    page = request.GET.get('page')
    books = paginator.get_page(page)
    return render(request, "store/category.html", {"book":books})

def get_book_category(request, id):
    book_ = Book.objects.filter(category_id=id)
    paginator = Paginator(book_, 10)
    page = request.GET.get('page')
    book = paginator.get_page(page)
    return render(request, "store/category.html", {"book":book})

def get_writer(request, id):
    wrt = get_object_or_404(Writer, id=id)
    book = Book.objects.filter(writer_id=wrt.id)
    context = {
        "wrt": wrt,
        "book": book
    }
    return render(request, "store/writer.html", context)

@app.route('/generate_otp', methods=['POST'])
def get_generate_otp(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)  # Replace YourForm with the actual form class
        if form.is_valid():
            user = request.POST.get('user')
            password = request.POST.get('pass')
            print(user)
            print(password)
            auth = authenticate(request, username=user, password=password)
            if auth is not None:
                login(request, auth)
                # return redirect('store:index')
            else:
            	messages.error(request, 'username and password doesn\'t match')
            # Process the form data
            # ...

            # Access form data using form.cleaned_data
            email = form.cleaned_data['email']
            email = request.POST.get('email')

    # Create a TOTP object using the secret key
            totp = pyotp.TOTP(SECRET_KEY)

    # Generate the OTP
            otp = totp.now()

    # Send OTP via email
            send_otp_email(email, otp)

        
    return render(request, "store/otp.html", {"form":form})	

def send_otp_email(email, otp):
    subject = "Your One-Time Password"
    body = f"Hello,\n\nYour OTP is: {otp}"

    msg = MIMEMultipart()
    msg['From'] = GMAIL_USERNAME
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        server.sendmail(GMAIL_USERNAME, email, msg.as_string())

@app.route('/submit_otp', methods=['POST'])        
def get_submit_otp(request):
    if request.user.is_authenticated:
        return redirect('store:index')
    else:
        if request.method == "POST":
            # user = request.POST.get('user')
            # print(user)
            # print(password)
            # password = request.POST.get('pass')
            # auth = authenticate(request, username=user, password=password)
            if auth is not None:
                login(request, auth)
                return redirect('store:index')
            else:
            	messages.error(request, 'username and password doesn\'t match')

    return render(request, "store/login.html")

# @app.route('/')        
# def login():
#     return render_template('store/login.html')


