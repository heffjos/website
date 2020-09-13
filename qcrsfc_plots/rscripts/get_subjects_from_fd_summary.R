library(tidyverse)

data <- read_csv("hcp_fd_summary.csv") %>%
  arrange(desc(mean_fd))

center <- floor(nrow(data) / 2)

index <- c(1:40, (center - 20):(center + 19), (nrow(data) - 39):nrow(data))
subjects <- data[index, ]

write_csv(subjects, "sample_subjects.csv")
              


