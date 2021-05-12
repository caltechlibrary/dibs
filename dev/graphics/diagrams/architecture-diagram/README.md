# DIBS architecture diagram

<p align="center"><img width="60%" src="https://raw.githubusercontent.com/caltechlibrary/dibs/main/dev/graphics/diagrams/dibs-architecture.svg">

The system overview diagram in [dibs-architecture.graffle](dibs-architecture.graffle) was created by Michael Hucka in May, 2021, using OmniGraffle 7.11.5 on a macOS 10.13.6 computer. The SVG version in [dibs-architecture.svg](dibs-architecture.svg) was produced using the following steps: 

<img width="400px" align="right"  src="https://github.com/caltechlibrary/dibs/blob/main/dev/graphics/diagrams/omnigraffle-export-options.png?raw=true"/>

1. Export from OmniGraffle to SVG format, using the options "transparent background" and `0`inch margin. (See screen image at the right.)
2. Run [svg-buddy](https://github.com/phauer/svg-buddy) on the SVG file produced from step #1. This will embed the fonts used in the SVG file, overcoming a limitation of OmniGraffle's SVG output. The following is the command line used:
    ```sh
    java -jar svg-buddy.jar dibs-architecture.svg
    ```

The architecture diagram contains, embedded within it, icons obtained from the Noun Project.  All are licensed under the Creative Commons [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/) license. Here are acknowledgments for the original artwork:

* [Book icon](https://thenounproject.com/search/?q=book&i=2289902) by [vigorn](https://thenounproject.com/vigorn/)
* [Book scanner icon](https://thenounproject.com/search/?q=book+scanner&i=3635943) by [Oleksandr Panasovskyi](https://thenounproject.com/a.panasovsky/)
* [Laptop icon](https://thenounproject.com/search/?q=laptop&i=3563257) by [Hey Rabbit](https://thenounproject.com/heyrabbit/)
* [Tablet icon](https://thenounproject.com/search/?q=tablet&i=205015) by [Emel Çelik](https://thenounproject.com/iconmood/)
