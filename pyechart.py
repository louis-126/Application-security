from pyecharts.charts import Bar


def bargraph(x, y):
    bar = Bar()
    bar.add_xaxis(x)
    bar.add_yaxis("Visitor", y)
    bar.render('templates/Appointment/charts.html')


def applicationbargraph(x, y):
    bar = Bar()
    bar.add_xaxis(x)
    bar.add_yaxis("People", y)
    bar.render('templates/ApplicationForm/dashboard.html')


def addressbargraph(x, y):
    bar = Bar()
    bar.add_xaxis(x)
    bar.add_yaxis("People", y)
    bar.render('templates/ApplicationForm/dashboard2.html')


def agerangebargraph(x, y):
    bar = Bar()
    bar.add_xaxis(x)
    bar.add_yaxis("People", y)
    bar.render('templates/ApplicationForm/dashboard3.html')

def monthlyQnbargraph(x, y):
    bar = Bar()
    bar.add_xaxis(x)
    bar.add_yaxis('Month',y)
    bar.render('templates/FAQ/monthlyQn.html')

def usernumber(x, y):
    bar = Bar()
    bar.add_xaxis(x)
    bar.add_yaxis('number',y)
    bar.render('templates/Admin/admin_dashboard.html')