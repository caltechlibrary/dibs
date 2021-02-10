<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Welcome to Caltech DIBS</title>
  </head>
  
  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('common/navbar.tpl')

      <div class="container text-center">
        <div class="row pt-3">
          <div class="col">
            <h1 class="mx-auto text-center" style="color: #FF6C0C">
              Welcome to Caltech DIBS
            </h1>
            <h2 class="mx-auto my-3 text-center text-info font-italic">
              The Caltech <strong>Di</strong>gital <strong>B</strong>orrowing <strong>S</strong>ystem
            </h2>
            <p class="pt-3"><strong>Caltech DIBS</strong> is an implementation of <a target="_blank" href="https://controlleddigitallending.org">Controlled Digital Lending</a>, allowing members of Caltech to borrow materials that are not otherwise available in e-book or other electronic formats.  The system was implemented in the year 2021 to help Caltech students and faculty during the global <a target="_blank" href="https://www.who.int/emergencies/diseases/novel-coronavirus-2019">COVID-19 pandemic.</a> Access to materials in Caltech DIBS is limited to current Caltech faculty, students and staff.</p>
          </div>
        </div>
        <div class="row justify-content-center pt-3">
          <div class="col-md-4 col-md-offset-4">
            <form action="{{base_url}}/login" method="post">
              <input class="my-1" name="email" type="text" placeholder="User" required autofocus/>
              <input class="my-1" name="password" type="password" placeholder="Password" required/><br>
              <input class="btn btn-primary my-2" value="Login" type="submit" />
            </form>
          </div>
        </div>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
