<footer class="footer bg-secondary text-center py-3 mt-5">
    <img alt="Caltech Library logo" title="Caltech Library" typeof="foaf:Image"
         class="footer-logo media-element file-block-original"
         src="https://www.library.caltech.edu/sites/default/files/logos/CLwhitewhiteVerticalwww.png">
    <div class="footer-text">
      <span class="text-white px-5">
        Mail Code 1-43, 1200 E California Blvd, Pasadena, CA 91125
      </span>
    </div>
    %if feedback_url:
    <span class="footer-feedback">
      <img src="{{base_url}}/static/megaphone-white.svg" height="25rem"">
      <a href="{{feedback_url}}" class="text-white ml-1">Give feedback</a>
    </span>
    %else:
    <span class="footer-feedback">
      <a href="{{base_url}}/about" class="text-white ml-1">About DIBS</a>
    </span>
    %end
</footer>
