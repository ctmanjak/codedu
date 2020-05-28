a=$(echo '123' | grep 'a')

b='123'

if [ $a ]; then
    echo 'good'
fi