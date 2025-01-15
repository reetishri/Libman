from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Student, Staff, Book, IssueBooks
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from datetime import datetime, timedelta



def welcome(request):
    return render(request, 'library/welcome.html')

def rules(request):
    return render(request, 'library/rules.html')

def contact(request):
    return render(request, 'library/contact.html')

def register(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        

        if user_type == 'student':
            password = request.POST.get('password')
            re_enter_password = request.POST.get('re_enter_password')
                  
        elif user_type == 'staff':
            password = request.POST.get('password1')
            re_enter_password = request.POST.get('re_enter_password1')

        else: 
            messages.error(request, 'Please select a user type.')
            return render(request, 'library/register.html')
        
        if password != re_enter_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'library/register.html')
            

        if user_type == 'student':
            student_name = request.POST.get('student_name')
            roll_no = request.POST.get('roll_no')
            department = request.POST.get('department')
            profile_picture = request.FILES.get('profile_picture')

            if not student_name or not roll_no or not department or not profile_picture:
                messages.error(request, 'All fields are required for student registration.')
                return render(request, 'library/register.html')

            if User.objects.filter(username=roll_no).exists():
                messages.error(request, 'Roll number already exists.')
                return render(request, 'library/register.html')

            user = User.objects.create_user(username=roll_no, password=password)
            student = Student(student_name=student_name, roll_no=roll_no, department=department, picture=profile_picture)
            student.save()
            messages.success(request, 'Student registered successfully!')
            return redirect('library:login')

        elif user_type == 'staff':
            staff_name = request.POST.get('staff_name')
            staff_id = request.POST.get('staff_id')

            if not staff_name or not staff_id:
                messages.error(request, 'All fields are required for staff registration.')
                return render(request, 'library/register.html')

            if User.objects.filter(username=staff_id).exists():
                messages.error(request, 'Staff ID already exists.')
                return render(request, 'library/register.html')

            user = User.objects.create_user(username=staff_id, password=password)
            staff = Staff(staff_name=staff_name, staff_id=staff_id)
            staff.save()
            messages.success(request, 'Staff registered successfully!')
            return redirect('library:login')

    return render(request, 'library/register.html')

def user_login(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        
        if user_type == 'staff':
            staff_id = request.POST.get('staff_id')
            password = request.POST.get('password1')
            
            try:
                staff=Staff.objects.get(staff_id=staff_id)
            except Staff.DoesNotExist:
                messages.error(request, 'Staff ID does not exist.')
                return render(request, 'library/login.html')
            
            user = authenticate(request, username=staff_id, password=password)
            
        elif user_type == 'student':
            roll = request.POST.get('roll_no')
            password = request.POST.get('password')  # Use the same name for the password field
            try:
                student=Student.objects.get(roll_no=roll)
            except Student.DoesNotExist:
                messages.error(request, 'Roll number does not exist.')
                return render(request, 'library/login.html')

            user = authenticate(request, username=roll, password=password)
            
            

        else:
            messages.error(request, 'Please select a user type.')
            return render(request, 'library/login.html')    

        if user is not None:
            login(request, user)
            request.session['user_type'] = user_type
            if user_type == 'student':
                return redirect('library:student_dashboard')
            elif user_type == 'staff':
                return redirect('library:staff_dashboard')
        else:
            messages.error(request, 'Incorrect credentials.')
            return render(request, 'library/login.html')

    return render(request, 'library/login.html')

@login_required(login_url='library:login')
def student_dashboard(request):
    if request.user.is_authenticated and request.session.get('user_type') == 'student':
        student = Student.objects.get(roll_no=request.user.username)
        issued_books = IssueBooks.objects.filter(roll_no=student)

        issued_books_with_days_remaining = []
        total_fine = 0
        for issue in issued_books:
            return_date = issue.issue_date + timedelta(days=15)
            days_remaining = (return_date - datetime.now().date()).days
            pending_fine = 0
            if days_remaining < 0:
                pending_fine = (datetime.now().date() - return_date).days * 2
                days_remaining = 0
            total_fine += pending_fine
            issued_books_with_days_remaining.append({
                'issue': issue,
                'days_remaining': days_remaining
            })

        context = {
            'student': student,
            'issued_books_with_days_remaining': issued_books_with_days_remaining,
            'total_fine': total_fine
        }
        return render(request, 'library/student_dashboard.html', context)
    else:
        return redirect('library:login')

@login_required(login_url='library:login')    
def staff_dashboard(request):
    if request.user.is_authenticated and request.session.get('user_type') == 'staff':
        staff = Staff.objects.get(staff_id=request.user.username)
        context = {
            'staff': staff,
        }
        return render(request, 'library/staff_dashboard.html', context)
    else:
        return redirect('library:login') 
    
def user_logout(request):
    print("Logout view START")  # Check if the view is being entered
    if 'student_id' in request.session:
        del request.session['student_id']
        if 'student_name' in request.session: #delete the name too
            del request.session['student_name']           
    logout(request) #django's logout function
    print("Session after logout:", request.session.items())
    print("Logout view END") # Check if the view is finishing
    return redirect('library:welcome')

@login_required(login_url='library:login')
def password_change(request):
    dash = 'library:staff_dashboard' if request.session.get('user_type') == 'staff' else 'library:student_dashboard'
    
    if request.method == 'POST':
        password = request.POST.get('password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            user = request.user  # Get the authenticated user

            if check_password(password, user.password):
                user.set_password(new_password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')
                return redirect(dash)
            else:
                messages.error(request, 'Incorrect current password.')
        else:
            messages.error(request, 'New passwords do not match.')

    return render(request, 'library/password_change.html', {'dash': dash})

@login_required(login_url='library:login')
def book_catalogue(request):
    dash = 'library:staff_dashboard' if request.session.get('user_type') == 'staff' else 'library:student_dashboard'
    books = Book.objects.all()  # Fetch all books from the database
    context = {
            'books': books,
            'dash': dash,
        }
    return render(request, 'library/book_catalogue.html', context)
    

@login_required(login_url='library:login')
def book_record(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        book_name = request.POST.get('book_name')
        book_id = request.POST.get('book_id')
        genre = request.POST.get('genre')
        book_cover = request.FILES.get('book_cover')

        print(f"Action: {action}")
        print(f"Book ID: {book_id}")

        if action == 'add':
            print("Adding book...")
            if not book_name or not book_id or not genre or not book_cover:
                messages.error(request, 'All fields are required to add a book.')
                return redirect('library:book_record')

            if Book.objects.filter(book_id=book_id).exists():
                messages.error(request, 'Book ID already exists.')
                return redirect('library:book_record')

            book = Book(book_name=book_name, book_id=book_id, genre=genre, book_cover=book_cover)
            book.save()
            messages.success(request, 'Book added successfully!')
            return redirect('library:book_record')

        elif action == 'remove':
            print("Removing book...")
            if not book_id:
                messages.error(request, 'Book ID is required to remove a book.')
                return redirect('library:book_record')

            try:
                book = Book.objects.get(book_id=book_id)
                print(f"Book found: {book}")
                book.delete()
                messages.success(request, 'Book removed successfully!')
            except Book.DoesNotExist:
                print("Book does not exist.")
                messages.error(request, 'Book ID does not exist.')
            return redirect('library:book_record')

    return render(request, 'library/book_record.html')



@login_required(login_url='library:login')
def issue_return(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        book_id = request.POST.get('book_id')
        roll_no = request.POST.get('roll_no') 

        try:
            book = Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            messages.error(request, 'Book ID does not exist.')
            return redirect('library:issue_return')

        if action == 'issue':
            if not roll_no:
                messages.error(request, 'Roll No is required to issue a book.')
                return redirect('library:issue_return')

            try:
                student = Student.objects.get(roll_no=roll_no)
            except Student.DoesNotExist:
                messages.error(request, 'Roll No does not exist.')
                return redirect('library:issue_return')
            
            if IssueBooks.objects.filter(book_id=book).exists():
                messages.error(request, 'Book is already issued.')
                
            else:        
                issu = IssueBooks(book_id=book, roll_no=student, issue_date=datetime.now())
                issu.save()
                messages.success(request, 'Book issued successfully!')

        elif action == 'return':
            if IssueBooks.objects.filter(book_id=book).exists():
                issu1 = IssueBooks.objects.get(book_id=book)
                issu1.delete()
                messages.success(request, 'Book returned successfully!')
            else:
                messages.error(request, 'Book is not issued.')

        return redirect('library:issue_return')

    return render(request, 'library/issue_return.html')

@login_required(login_url='library:login')
def book_enquiry(request):
    if request.method == 'POST':
        book_id = request.POST.get('book_id')

        try:
            book = Book.objects.get(book_id=book_id)
        except Book.DoesNotExist:
            messages.error(request, 'Book ID does not exist.')
            return redirect('library:book_enquiry')

        try:
            issue=IssueBooks.objects.get(book_id=book.book_id)
        except IssueBooks.DoesNotExist:
            messages.error(request, 'The book has not been issued.')
            issue=None
        
        if issue:
            student = Student.objects.get(roll_no=issue.roll_no.roll_no)
        else:
            student=None
        

        context = {
            'book': book,
            'issue': issue,
            'student': student,
        }
        return render(request, 'library/book_enquiry.html', context)

    return render(request, 'library/book_enquiry.html')


@login_required(login_url='library:login')
def student_enquiry(request):
    if request.method == 'POST':
        roll_no = request.POST.get('roll_no')

        try:
            student = Student.objects.get(roll_no=roll_no)
        except Student.DoesNotExist:
            messages.error(request, 'Roll No does not exist.')
            return redirect('library:student_enquiry')

        issued_books = IssueBooks.objects.filter(roll_no=student)
        context = {
            'student': student,
            'issued_books': issued_books,
        }
        return render(request, 'library/student_enquiry.html', context)

    return render(request, 'library/student_enquiry.html')
 

    