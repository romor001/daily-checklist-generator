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
  set page(
    paper: "a4",
    margin: (left: 2.0cm, right: 2.0cm, top: 2.0cm, bottom: 2.0cm),
  )
  
  // Set font family to Lato
  set text(font: "Lato")
  
  // Headers
  show heading: set text(font: "Lato")
  
  // Header with logo and title
  set page(
    header: {
      grid(
        columns: (auto, 1fr),
        gutter: 1em,
        if logo != none {
          image(logo, width: 2cm)
        },
        align(right + horizon)[
          #text(size: 1.5em, weight: "bold")[#title]
        ]
      )
      line(length: 100%)
    }
  )

  // Main body
  body
}