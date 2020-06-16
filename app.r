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
      textInput("marking_scheme","Marking scheme (+a/-b)",placeholder = "+3/-1",value = "+3/-1"),
      dateInput("date1", "Start Date", value = Sys.Date()),
      dateInput("date2", "End Date", value = Sys.Date()+7),
      actionButton(
        "go",
        "Upload Quiz",
        class = "btn-primary"
      )
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
  start_date <- reactive({
    input$date1
  })
  end_date <- reactive({
    input$date2
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
  quiz_name <- reactive({
    input$quiz_name
  })
  qm_name <- reactive({
    input$qm_name
  })
  quiz_code <- reactive({
    sc <- format(Sys.Date(), format="%m %d") %>% str_replace_all(" ", "")
    paste0(sc,
           quiz_name() %>% substring(1, 1) %>% toupper(),
           qm_name() %>% substring(1, 1) %>% toupper())
  })
  quiz_data <- reactive({
    req(input$file$datapath) %>% read_csv() %>%  as.tibble() -> a
    colnames(a) <-(c("question", "A", "B", "C", "D","correct"))
    a %>%  mutate(quiz_code = quiz_code())->a
    a
  })
  
  quiz_info <- reactive({
    quiz_info <- data.frame(
      quiz_code = quiz_code(), 
      quiz_name = quiz_name(),
      qm_name = qm_name(),
      total_question = quiz_data() %>% nrow(),
      positive_marks = positive_marks(),
      negative_marks = negative_marks(),
      upload_date = upload_date(),
      start_date = start_date(),
      end_date = end_date()
    )
    quiz_info
  })
  
  output$input_file <- DT::renderDataTable({
    quiz_data() %>% select(c("question","A","B","C","D","correct")) %>% datatable(options = list(pageLength = 15, 
                                                                                                  lengthChange = FALSE,
                                                                                                  searching = FALSE))
  })
  
  output$quiz_info <- DT::renderDataTable({
    c1 <- c("Quiz","Quiz Master","Quiz Code","Marking Scheme","Start on","Ends on")
    c2 <- c(quiz_name(),qm_name(),quiz_code(),marking(),start_date() %>% as.character(),end_date() %>% as.character())
    c1 %>% 
      as.tibble() %>% 
      cbind(c2 %>% as.tibble()) %>% 
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
    else if(is.null(quiz_name())){
      showNotification("please fill Quiz name before uploading")
      return()
    }
    else if(is.null(quiz_data())){
      showNotification("please load the csv file before uploading")
      return()
    }
    else{
      con <- dbConnect(drv = RMariaDB::MariaDB(),
                       dbname = DB_NAME,
                       host = HOST_NAME,
                       username = USER_NAME,
                       password = PASSWORD)

      dbAppendTable(conn = con, name = "quiz_data", value = as.data.frame(quiz_data()))
      dbAppendTable(conn = con, name = "quiz_info", value = as.data.frame(quiz_info()))
      dbDisconnect(con)
      showNotification("file uploaded successfully")
    }

  })
  
}

shinyApp(ui, server)
