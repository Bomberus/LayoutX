```plantuml format="png" classes="uml" alt="Architecture" title="Architecture"

@startuml

skinparam component {
  FontSize 13
  BackgroundColor<<Apache>> Red
  BorderColor<<Apache>> #FF6655
  FontName Courier
  BorderColor black
  BackgroundColor gold
  ArrowFontName Impact
  ArrowColor #FF6655
  ArrowFontColor #777777
}

Application - [Registry]
Layout ..> [View] 
[Registry] <..> [View]
[View] <..> () Store
[View] <..> [Widget]
[Widget] ..> [Widget]

@enduml

```

## Application

The Application is a singleton and the single entry to the framework itself. It is mostly used to initially setup the framework.

## Registry

The Registry is an internal data tree and keeps the parent-child information of each view and their connected widgets. It is managed by the views.

## View

A View represents a GUI window. It can have its own store or uses the application default store. Each view has it own layout declaration and dynamically creates its widgets according to it.

## Widget

A widget extends the standard tkinter widget with additional capabilities like initializing two-way binding with the store. It holds a reference to the Application, parent view and store.
Via lifecycle methods the behavior of a widget at runtime can be controlled.

## Store

The store keeps all business data at a centralized place. It is powered by RxPY and emulates the Redux pattern. You can define reducers to simplify the data manipulation. All connected widgets are automatically informed about any changes via subscriptions.

## Layout

Written in Pug, it is the declarative representation of the UI and holds all display releated information.