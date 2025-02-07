// Define custom task checkboxes
#let task(description, content, indent: 0) = {
  // Create indentation based on level
  h(0.7em + indent * 1.5em)
  box(width: 1em, height: 1em, stroke: black)
  h(0.5em)
  content
  linebreak()
}

#let project(
  title: "",
  logo: none,
  body,
) = {
  // Set the document's basic properties
  set document(author: "", title: title)
  
  // Define header content that will be used on each page
  let header-content = {    
    grid(
      columns: (1fr, auto),  // Swapped: first column flexible, second fixed
      gutter: 1em,
      align(left + horizon)[
        #text(size: 1.5em, weight: "bold")[#title]
      ],
      if logo != none {
        align(right)[
          #image(logo, width: 2cm)
        ]
      }
    )
  }
  
  // Set page properties including the header for all pages
  set page(
    paper: "a4",
    margin: (left: 0cm, right: 0cm, top: 6cm, bottom: 0cm),
    header: header-content,
    header-ascent: 5%
  )
  
  // Set font family to Lato for the whole document
  set text(font: "Lato")
  
  // Headers style
  show heading: set text(font: "Lato")

  // Main content
  body
}