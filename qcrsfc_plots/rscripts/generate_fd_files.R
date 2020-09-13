library(tidyverse)

data_dir <- "/rcc/stor1/depts/neurology/users/jheffernan/hcp/HCP_1200"
subjects <- dir(data_dir)
func <- "rfMRI_REST1_LR"

data <- tibble(subject = subjects, func = func) %>%
  mutate(fd_file = file.path(data_dir, subject, "MNINonLinear/Results", func, "framewise_displacement.txt")) %>%
  filter(file.exists(fd_file)) %>%
  mutate(fd_info = map(fd_file, read_csv, col_names = "fd")) %>%
  unnest(c(fd_info)) %>%
  group_by(subject, func) %>%
  mutate(vol = 1:n()) %>%
  ungroup() %>%
  select(subject, func, fd, vol)

write_csv(data, "hcp_fd.csv")

data %>%
  group_by(subject, func) %>%
  summarize(mean_fd = mean(fd),
            max_fd = max(fd),
            median_fd = median(fd)) %>%
  ungroup() %>%
  write_csv("hcp_fd_summary.csv")


