# Backend

- TODO: [TODO.md](./TODO.md)

## Commands

### For development

- initialize database (`drop` optional)

```shell
flask --app backend/app initdb <--drop>
```

- generate fake data

```shell
flask --app backend/app forge
```

## How to run

- Makefile

Which equals to `python ./backend/app.py`.

```shell
make
```

- flask shell (not recommanded)

In this way, SocketIO may not work connectly.

```shell
flask --app backend/app run
```
