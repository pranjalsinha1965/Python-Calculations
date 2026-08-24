Remove-Item deployment\lambda-package -Recurse -Force -ErrorAction SilentlyContinue

New-Item -ItemType Directory -Force deployment\lambda-package

Copy-Item core deployment\lambda-package\core -Recurse -Force

Copy-Item api deployment\lambda-package\api -Recurse -Force

Remove-Item deployment\beam-calculator-lambda.zip -Force -ErrorAction SilentlyContinue

Compress-Archive `
    -Path deployment\lambda-package\* `
    -DestinationPath deployment\beam-calculator-lambda.zip `
    -Force