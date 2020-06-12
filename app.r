library(shiny)
library(tidyverse)
library(DBI)
library(RMariaDB)
library(DT)
ui <- fluidPage(
  headerPanel(title = "SIRPI QUIZ BOT"),
  sidebarLayout(
    sidebarPanel(
      fileInput("file", "Upload the csv file"),
      textInput("quiz_name","Quiz",placeholder = "type here the name of the quiz"),
      textInput("qm_name","Quiz Master",placeholder = "type here the name of the quiz master"),
      textInput("marking_scheme","please type the marking scheme in the format +a/-b",placeholder = "+3/-1"),
      actionButton("go", "Upload quiz",style="width:100% !important;")
    ),
    mainPanel(
      DT::dataTableOutput('quiz_info'),
      DT::dataTableOutput('input_file')
    )
  )
)

server <- function(input, output) {
  upload_date <- reactive({
    Sys.Date()
  })
  marking <- reactive({
    input$marking_scheme
  })
  positive_marks<- reactive({
    marking() %>% strsplit("/") %>% .[[1]] %>% parse_integer() %>% .[[1]]
  })
  negative_marks<- reactive({
    marking() %>% strsplit("/") %>% .[[1]] %>% parse_integer() %>% .[[2]]
  })
  quiz_title <- reactive({
    input$quiz_name
  })
  qm_name <- reactive({
    input$qm_name
  })
  quiz_code <- reactive({
    paste0(format(Sys.time(), "%y"),
           format(Sys.time(), "%m"),
           format(Sys.time(), "%d"),
           format(Sys.time(), "%H"),
           quiz_title() %>% substring(1, 1) %>% toupper(),
           qm_name() %>% substring(1, 1) %>% toupper())
  })
  quiz_table <- reactive({
    req(input$file$datapath) %>% read_csv() %>%  as_tibble() -> a
    colnames(a) <-(c("Question", "A", "B", "C", "D","Correct"))
    a %>%
      mutate(quiz_name = quiz_title(),
             qm_name = qm_name(),
             quiz_code = quiz_code(),
             positive_marks = positive_marks(),
             negative_marks = negative_marks(),
             upload_date = upload_date()) -> a
    a
  })
  
  output$input_file <- DT::renderDataTable({
    quiz_table() %>% select(c("Question","A","B","C","D","Correct")) %>% datatable()
  })
  
  output$quiz_info <- DT::renderDataTable({
    c1 <- c("Quiz","Quiz Master","Quiz Code","Marking Scheme")
    c2 <- c(quiz_title(),qm_name(),quiz_code(),marking())
    c1 %>% 
      as_tibble() %>% 
      cbind(c2 %>% as_tibble()) %>% 
      datatable( rownames = F,colnames = '',
                 options = list(dom = 't',
                                columnDefs = list(list(className = 'dt-center', 
                                                       targets = "_all"))
                 ))
    
  })
  observeEvent(input$go,{
    if(is.null(qm_name())){
      showNotification("please fill Quiz Master name before uploading")
      return()
    }
    else if(is.null(quiz_title())){
      showNotification("please fill Quiz name before uploading")
      return()
    }
    else if(is.null(quiz_table())){
      showNotification("please load the csv file before uploading")
      return()
    }
    else{
      con <- dbConnect(drv = RMariaDB::MariaDB(),
                       dbname = DB_NAME,
                       host = HOST_NAME,
                       username = USER_NAME,
                       password = PASSWORD)
      
      dbAppendTable(conn = con, name = "quiz_table", value = as.data.frame(quiz_table()))
      dbDisconnect(con)
      showNotification("file uploaded successfully") 
    }

  })

}

shinyApp(ui, server)