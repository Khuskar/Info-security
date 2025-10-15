first=john
last=doe
dob=19900512 
year=1990
month=05
day=12
out="custom_passwords.txt"
: > "$out"

echo "${first}${last}" >> "$out"
echo "${first}${year}" >> "$out"
echo "${first}${day}${month}" >> "$out"
echo "${first}${last}${year}" >> "$out"
echo "${first}123" >> "$out"
echo "${first}!" >> "$out"
echo "${last}${year}" >> "$out"
echo "${last}${day}" >> "$out"
echo "${first}${last}123" >> "$out"
echo "${first}.${last}" >> "$out"
echo "${first}_${last}" >> "$out"
echo "${first}${month}${day}" >> "$out"
echo "${dob}" >> "$out"
Fcap="$(tr '[:lower:]' '[:upper:]' <<< "${first:0:1}")${first:1}"
Lcap="$(tr '[:lower:]' '[:upper:]' <<< "${last:0:1}")${last:1}"
echo "${Fcap}${last}" >> "$out"
echo "${first}${Lcap}" >> "$out"
for suf in 123 1234 2020 2021 "!"; do
  echo "${first}${suf}" >> "$out"
  echo "${last}${suf}" >> "$out"
done
sort -u "$out" -o "$out"
echo "Generated $(wc -l < "$out") candidates in $out"
