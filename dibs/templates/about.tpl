<!DOCTYPE html>
<html lang="en" style="height: 100%">
  %include('common/banner.html')
  <head>
    %include('common/standard-inclusions.tpl')
    <link rel="stylesheet" href="https://use.fontawesome.com/releases/v5.6.0/css/all.css">
    <title>Caltech DIBS</title>
  </head>

  <body style="height: 100%">
    <div style="position: relative; padding-bottom: 3em; height: 100%">
      %include('common/navbar.tpl')

      <div class="container">
        <h1 class="mx-auto text-center pt-3" style="color: #FF6C0C">
          The Caltech Library <strong>Di</strong>gital <strong>B</strong>orrowing <strong>S</strong>ystem
        </h1>
        <p class="my-3"><strong>Caltech DIBS</strong> is an implementation of <a target="_blank" href="https://controlleddigitallending.org">Controlled Digital Lending</a>, allowing members of Caltech to borrow materials that are not otherwise available in e-book or other electronic formats. The system was implemented in the year 2021 to help Caltech students and faculty during the global <a target="_blank" href="https://www.who.int/emergencies/diseases/novel-coronavirus-2019">COVID-19 pandemic</a>.</p>

        <p align="center"><i class="fas fa-question-circle fa-2x" style="vertical-align: middle"></i> <span style="vertical-align: middle">Visit the is <a target="_blank" href="https://caltechlibrary.github.io/dibs/">online help documentation</a> to learn more about how to use DIBS.</span></p>

        <p>DIBS is <a href="https://en.wikipedia.org/wiki/Open-source_software">open-source software</a>. The source code is freely available <a href="https://github.com/caltechlibrary/dibs">from GitHub</a> under the terms of a <a href="https://github.com/caltechlibrary/dibs/blob/main/LICENSE">BSD 3-clause license</a>.  It was implemented by <a href="https://github.com/mhucka">Michael Hucka</a>, <a href="https://github.com/rsdoiel">Robert Doiel</a>, <a href="https://github.com/t4k">Tommy Keswick</a> and <a href="https://github.com/nosivads">Stephen Davison</a> from the Caltech Library's <a href="https://www.library.caltech.edu/staff?&field_directory_department%5B0%5D=754">Digital Library Development team</a>. DIBS is written primarily in Python and uses the <a href="http://universalviewer.io">Universal Viewer</a> for displaying scanned books and other items.  The icons used on DIBS pages are from <a href="https://fontawesome.com">Font Awesome</a>, with additional special icons created by <a href="https://thenounproject.com/roywj/">Royyan Wijaya</a> and <a href="https://thenounproject.com/thezyna/">Scott Desmond</a> for the <a href="https://thenounproject.com">Noun Project</a>.</p>
      </div>

      %include('common/footer.html')
    </div>
  </body>
</html>
