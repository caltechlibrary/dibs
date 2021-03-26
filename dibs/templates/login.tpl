<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Welcome to Caltech DIBS</title>
  </head>
  
  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container main-container">
        <div class="row pt-3">
          <div class="col">
            <h1 class="mx-auto text-center caltech-color">
              Welcome to Caltech DIBS
            </h1>
            <h2 class="mx-auto my-3 text-center text-info font-italic">
              The Caltech <strong>Di</strong>gital <strong>B</strong>orrowing <strong>S</strong>ystem
            </h2>
            <p class="pt-3 w-100"><strong>Caltech DIBS</strong> is an implementation of <a target="_blank" href="https://controlleddigitallending.org">Controlled Digital Lending</a>, allowing members of Caltech to borrow materials that are not otherwise available in e-book or other electronic formats.  The system was implemented in the year 2021 to help Caltech students and faculty during the global <a target="_blank" href="https://www.who.int/emergencies/diseases/novel-coronavirus-2019">COVID-19 pandemic.</a> Access to materials in Caltech DIBS is limited to current Caltech faculty, students and staff.</p>
          </div>
        </div>
        <div class="row pt-2 mx-auto text-center">
          <form class="form-horizontal col-sm-12" action="{{base_url}}/login" method="post">

            %if get('login_failed', False):
            <div classs="form-group">
              <span class="error text-danger">Ooops! Incorrect user or password. Try again?</span>
            </div>
            %end

            <div class="form-group">
              <label class="col-form-label col-sm-5 text-left">DIBS user</label>
              <input class="form-control col-sm-5 mx-auto" name="email" type="text" autocomplete="off"
                     placeholder="User" required autofocus/>
            </div>

            <div class="form-group">
              <label class="col-form-label col-sm-5 text-left">DIBS password</label>
              <input class="form-control col-sm-5 mx-auto" name="password" type="text" autocomplete="off"
                     placeholder="Password" required/>
            </div>

            <input class="btn btn-primary my-2" value="Login" type="submit" />
          </form>
        </div>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
