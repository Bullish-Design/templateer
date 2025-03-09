generate() {
  copier copy -f --trust -r HEAD "$1" "$2" \
    -d testing=true \
    -d project_name="Bullish-Design Testing" \
    -d project_description='Testing this great template' \
    -d author_fullname="Bullish Design" \
    -d author_username="Bullish-Design" \
    -d author_email="bullishdesignengineering@gmail.com" \
    -d insiders=true \
    -d public_release=false
}
