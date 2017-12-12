# mooseherding

Various python-related tools to automate the creation and extraction of FAMIX/MSE information from Java projects in git repositories.

Current version tested under Windows 10. 

Related run-time tools include Doris (executable .jar) and a Pharo-VM with the correct image, e.g., `Interface_Clients_CommandLineHandler.59.image`
(not yet in this repo).

The tools also use `iconv` because of [this issue with UTF-8](https://github.com/feenkcom/jdt2famix/issues/20).

Internal documentation: https://docs.google.com/document/d/1A-S9vWmhyk0raZT5aKxVfq79tY1R2koua53QSlQorRM/edit
