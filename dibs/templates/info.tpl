<!DOCTYPE html>
<html lang="en">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <title>Welcome to DIBS</title>
 </head>

  <body>
    <div class="page-content">
      %include('common/navbar.tpl')

      <div class="container main-container">
        <h1 class="mx-auto text-center pt-3 caltech-color">
          Welcome to Caltech DIBS
        </h1>
        <h2 class="mx-auto my-3 text-center text-info font-italic">
          The Caltech Library <strong>Di</strong>gital <strong>B</strong>orrowing <strong>S</strong>ystem
        </h2>
        <p class="my-3"><strong>Caltech DIBS</strong> is an implementation of <a target="_blank" href="https://controlleddigitallending.org">Controlled Digital Lending</a>, allowing members of Caltech to borrow materials that are not otherwise available in e-book or other electronic formats. Access to materials in Caltech DIBS is limited to current Caltech faculty, students and staff.</p>
        <p class="my-3">
          The following policies are implemented by the system:
          <ol>
            <li class="my-2">The number of copies of each item is determined by the number of physical copies of the corresponding printed work that the Caltech Library has pulled from the shelves. (This is typically a very small number.)</li>
            <li class="my-2">Each user may borrow only one item total from the system at any given time.</li>
            <li class="my-2">After returning an item, a user cannot borrow that same item again for a period of {{reloan_wait_time}}. They can, however, borrow other items immediately.</li>
          </ol>
        </p>
        <p class="my-3">
          Users are expected to follow the <a href="https://www.gradoffice.caltech.edu/current/community-standards/honor-code">Caltech Honor Code</a> and abide by these policies, and to avoid efforts to copy the materials or circumvent restrictions imposed by DIBS.  
        </p>
      </div>

      %include('common/footer.tpl')
    </div>
  </body>
</html>
